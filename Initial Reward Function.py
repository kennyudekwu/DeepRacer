# Imports
import math

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

def reward_function(params):
    # Define Weightings
    ON_TRACK_WEIGHTING             = 0.05 # REDUCE 
    DISTANCE_FROM_CENTRE_WEIGHTING = 0.10
    CONTOLLED_SPEED_WEIGHTING      = 0.05
    SPEED_WEIGHTING                = 0.35
    PROGRESS_WEIGHTING             = 0.45

    # Read input variables
    all_wheels_on_track = params['all_wheels_on_track']
    closest_waypoints = params['closest_waypoints']
    distance_from_center = params['distance_from_center']
    steps = params["steps"]
    progress = params["progress"]
    heading = params['heading']
    speed = params['speed']
    track_width = params['track_width']
    waypoints = params['waypoints']
    is_crashed = params['is_crashed']
    is_offtrack = params['is_offtrack']
    
    def progress_reward(all_wheels_on_track, steps, speed, progress):
        if all_wheels_on_track and steps > 0:
            reward = ((progress / steps) * 100) + (speed**2)
        else:
            reward = 0.01
            
        return max(1, float(reward))

    def distance_from_center_of_road_reward(track_width, distance_from_center):
        # Middle Track Band and Track Boundary
        MIDDLE_TRACK_BAND = 0.1 * track_width
        TRACK_BOUNDARY = 0.5 * track_width

        # Give higher reward if the car is in middle track band
        if distance_from_center <= MIDDLE_TRACK_BAND:
            # Fixed reward staying in middle
            reward = 1.0
        elif distance_from_center <= TRACK_BOUNDARY:
            # reward agent eventhough it's at track boundary as current action might be the most optimal for specific episode
            reward = 1.0 - 0.5*(distance_from_center / TRACK_BOUNDARY)
        else:
            reward = 0
        return reward
    
    def controlled_curve_speed_reward(waypoints, closest_waypoints, heading, speed):
        prev_point = waypoints[closest_waypoints[0]]
        next_point = waypoints[closest_waypoints[1]]
        track_direction = math.degrees(math.atan2(next_point[1] - prev_point[1], next_point[0] - prev_point[0]))
        direction_diff = abs(heading - (track_direction * 180.0 / math.pi))

        if direction_diff > 15 and speed > 3: # incentivize throttling at tight bends
            reward = 0.6
        else:
            reward = 1.0
        return reward
    
    def speed_reward(speed):
        MAX_SPEED = 4
        reward = speed/MAX_SPEED
        print("speed_reward: {}".format(reward))
        return reward
    
    def on_track_reward(all_wheels_on_track):
        if not all_wheels_on_track:
            reward = 0.06 # Minimum Reward
        else:
            reward = 1.0 # Maximum Reward
        print("on_track_reward: {}".format(reward))
        return reward
    
    reward = 0
    reward += ON_TRACK_WEIGHTING             * on_track_reward(all_wheels_on_track)
    reward += DISTANCE_FROM_CENTRE_WEIGHTING * distance_from_center_of_road_reward(track_width, distance_from_center)
    reward += CONTOLLED_SPEED_WEIGHTING      * controlled_curve_speed_reward(waypoints, closest_waypoints, heading, speed)
    reward += SPEED_WEIGHTING                * speed_reward(speed)
    reward += PROGRESS_WEIGHTING             * progress_reward(all_wheels_on_track, steps, speed, progress)
	
    # model should not get any reward at all if crashed or not on track
    if is_crashed or is_offtrack:
        return 0
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
