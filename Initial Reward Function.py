def reward_function(params):
    '''
    In @params object
    {
        "all_wheels_on_track": Boolean,        # flag to indicate if the agent is on the track
        "x": float,                            # agent's x-coordinate in meters
        "y": float,                            # agent's y-coordinate in meters
        "closest_objects": [int, int],         # zero-based indices of the two closest objects to the agent's current position of (x, y).
        "closest_waypoints": [int, int],       # indices of the two nearest waypoints.
        "distance_from_center": float,         # distance in meters from the track center 
        "is_crashed": Boolean,                 # Boolean flag to indicate whether the agent has crashed.
        "is_left_of_center": Boolean,          # Flag to indicate if the agent is on the left side to the track center or not. 
        "is_offtrack": Boolean,                # Boolean flag to indicate whether the agent has gone off track.
        "is_reversed": Boolean,                # flag to indicate if the agent is driving clockwise (True) or counter clockwise (False).
        "heading": float,                      # agent's yaw in degrees
        "objects_distance": [float, ],         # list of the objects' distances in meters between 0 and track_length in relation to the starting line.
        "objects_heading": [float, ],          # list of the objects' headings in degrees between -180 and 180.
        "objects_left_of_center": [Boolean, ], # list of Boolean flags indicating whether elements' objects are left of the center (True) or not (False).
        "objects_location": [(float, float),], # list of object locations [(x,y), ...].
        "objects_speed": [float, ],            # list of the objects' speeds in meters per second.
        "progress": float,                     # percentage of track completed
        "speed": float,                        # agent's speed in meters per second (m/s)
        "steering_angle": float,               # agent's steering angle in degrees
        "steps": int,                          # number steps completed
        "track_length": float,                 # track length in meters.
        "track_width": float,                  # width of the track
        "waypoints": [(float, float), ]        # list of (x,y) as milestones along the track center
    }
    '''
    # Imports
    import math

    # Define Weightings
    ON_TRACK_WEIGHTING             = 0.11
    DISTANCE_FROM_CENTRE_WEIGHTING = 0.05
    DIRECTION_WEIGHTING            = 0.09
    STEERING_WEIGHTING             = 0.09
    THROTTLING_WEIGHTING           = 0.11
    KEEP_LEFT_WEIGHTING            = 0.02
    PROGRESS_WEIGHTING             = 0.37
    SPEED_WEIGHTING                = 0.16

    # Read input variables
    all_wheels_on_track = params['all_wheels_on_track']
    x = params['x']
    y = params['y']
    closest_waypoints = params['closest_waypoints']
    distance_from_center = params['distance_from_center']
    is_left_of_center = params['is_left_of_center']
    heading = params['heading']
    progress = params['progress']
    speed = params['speed']
    steering_angle = params['steering_angle']
    steps = params['steps']
    track_width = params['track_width']
    waypoints = params['waypoints']
    
    
    def distance_from_center_of_road_reward(track_width, distance_from_center):
        # Middle Track Band and Track Boundary
        MIDDLE_TRACK_BAND = 0.1 * track_width
        TRACK_BOUNDARY = 0.5 * track_width

        # Give higher reward if the car is in middle track band
        if distance_from_center <= MIDDLE_TRACK_BAND:
            # Fixed reward staying in middle
            reward = 1.0
        elif distance_from_center <= TRACK_BOUNDARY:
            reward = 1.0 - (distance_from_center / TRACK_BOUNDARY)
        else:
            reward = 0
        return reward
    
    def direction_reward(waypoints, closest_waypoints, heading):
        next_point = waypoints[closest_waypoints[1]]
        prev_point = waypoints[closest_waypoints[0]]
        direction = math.atan2(next_point[1] - prev_point[1], next_point[0] - prev_point[0])
        direction = math.degrees(direction)
        direction_diff = abs(direction - heading)

        # Find the absolute difference between the track direction and the car's heading
        direction_diff = abs(params['heading'] - direction)
        # Use a nonlinear penalty for direction difference. The larger the difference, the smaller the reward.
        reward = 1.0 - (direction_diff / 180.0)  # normalized to [0, 1]
        print("direction_reward: {}".format(reward))
        return reward
    
    def on_track_reward(all_wheels_on_track):
        if not all_wheels_on_track:
            reward = 0.01 # Minimum Reward
        else:
            reward = 1.0 # Maximum Reward
        print("on_track_reward: {}".format(reward))
        return reward
        
    def steering_reward(steering_angle):
        # Penalize reward the car is steering too much (your action space will matter)
        ABS_STEERING_THRESHOLD = 30 # This should be the maximum absolute value from your action space.
        steering_penalty = abs(steering_angle) / ABS_STEERING_THRESHOLD
        reward = 1.0 - steering_penalty
        print("steering_reward: {}".format(reward))
        return reward
        
    def keep_left_reward(is_left_of_center):
        if is_left_of_center:
            reward = 1.0
        else:
            reward = 0.0
        print("keep_left_reward: {}".format(reward))
        return reward

    def throttling_reward(steering_angle, speed):
        THROTTLING_PARAM = 0.1
        if speed + THROTTLING_PARAM * abs(steering_angle) < 4.0:
            reward = 1.0
        elif speed + THROTTLING_PARAM * abs(steering_angle) < 5.0:
            reward = 0.5
        else:
            reward = 0
        print("throttling_reward: {}".format(reward))
        return reward
    
    def progress_reward(progress, steps):
        PROGRESSION_RATE = 0.05
        reward = (progress/100)**2 * (1/(PROGRESSION_RATE * math.log(steps + 1) + 1))
        print("progress_reward: {}".format(reward))
        return reward
    
    def speed_reward(speed):
        MAX_SPEED = 5.0
        normalized_speed = (speed / MAX_SPEED)**2 # Quadratic function accounting for more effect per unit change in speed

        # Ensure the normalized speed is capped at 1.0 in case we quote the max speed wrongly
        reward = min(1.0, normalized_speed)
        print("speed_reward: {}".format(reward))
        return normalized_speed
    
    reward = 0
    reward += ON_TRACK_WEIGHTING             * on_track_reward(all_wheels_on_track)
    reward += DISTANCE_FROM_CENTRE_WEIGHTING * distance_from_center_of_road_reward(track_width, distance_from_center)
    reward += DIRECTION_WEIGHTING            * direction_reward(waypoints, closest_waypoints, heading)
    reward += STEERING_WEIGHTING             * steering_reward(steering_angle)
    reward += THROTTLING_WEIGHTING           * throttling_reward(steering_angle, speed)
    reward += PROGRESS_WEIGHTING             * progress_reward(progress, steps)
    reward += KEEP_LEFT_WEIGHTING            * keep_left_reward(is_left_of_center)
    reward += SPEED_WEIGHTING                * speed_reward(speed)
	
    return float(reward)

########    
# TEST #
########

test_state = {
    "all_wheels_on_track": True,                    # flag to indicate if the agent is on the track
    "x": 5.5,                                       # agent's x-coordinate in meters
    "y": 10.5,                                      # agent's y-coordinate in meters
    "closest_objects": [0, 1],                      # zero-based indices of the two closest objects to the agent's current position of (x, y).
    "closest_waypoints": [0, 1],                    # indices of the two nearest waypoints.
    "distance_from_center": 0.4,                    # distance in meters from the track center 
    "is_crashed": False,                            # Boolean flag to indicate whether the agent has crashed.
    "is_left_of_center": True,                      # Flag to indicate if the agent is on the left side to the track center or not. 
    "is_offtrack": False,                           # Boolean flag to indicate whether the agent has gone off track.
    "is_reversed": False,                           # flag to indicate if the agent is driving clockwise (True) or counter clockwise (False).
    "heading": 10.3,                                # agent's yaw in degrees
    "objects_distance": [10.2],                     # list of the objects' distances in meters between 0 and track_length in relation to the starting line.
    "objects_heading": [120.3],                     # list of the objects' headings in degrees between -180 and 180.
    "objects_left_of_center": [True, True],         # list of Boolean flags indicating whether elements' objects are left of the center (True) or not (False).
    "objects_location": [(16.2, 32.1),(5.1, 22.8)], # list of object locations [(x,y), ...].
    "objects_speed": [0],                           # list of the objects' speeds in meters per second.
    "progress": 50.2,                               # percentage of track completed
    "speed": 5,                                     # agent's speed in meters per second (m/s)
    "steering_angle": 21,                           # agent's steering angle in degrees
    "steps": 0,                                     # number steps completed
    "track_length": 35.2,                           # track length in meters.
    "track_width": 1.3,                             # width of the track
    "waypoints": [(10.3, 12.4), (5.1, 6.4)]         # list of (x,y) as milestones along the track center
}
 
print("End reward: {}".format(reward_function(test_state)))
