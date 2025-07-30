from system.quadruped.parameters.ik_parameters import IKParameters

def get_pose_standing(): 
    ik_parameters: IKParameters = IKParameters()   
    ik_parameters.roll = 0
    ik_parameters.pitch = 0
    ik_parameters.yaw = 0
    ik_parameters.side_translation = 0
    ik_parameters.forward_translation = 0
    ik_parameters.height_translation = (ik_parameters.height_translation_min + ik_parameters.height_translation_max) / 2    
    return ik_parameters

def get_pose_sit(self):
    ik_parameters: IKParameters = IKParameters()   
    ik_parameters.roll = 0
    ik_parameters.pitch = 0
    ik_parameters.yaw = 0
    ik_parameters.side_translation = 0
    ik_parameters.forward_translation = 0
    ik_parameters.height_translation = ik_parameters.height_translation_min    
    return ik_parameters