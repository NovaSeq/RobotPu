
class Parameters(object):
    def __init__(self):
        self.w_t, self.j_t, self.l_s = 16, 27, 45
        # degrees of freedom    
        self.dof = 6
        # servo error 
        self.s_err = [0.0] * self.dof
        # servo control vector
        self.s_ct = [0.0] * self.dof
        # current servo target values
        self.s_tg = [90.0] * self.dof
        # servo trim vector
        self.s_tr = [-5, -0.0, -5, -0.0, -9.0, 0.0] + [0.0] * (self.dof - 6)
        # turning directions of each grid of point clouds
        self.ep_dir = [-1.0, -0.7, 0.7, 1.0]
        self.ep_size = len(self.ep_dir)
        self.ep_dis = [500.0] * self.ep_size
        self.ep_mid2 = int(self.ep_size * 0.5)
        self.ep_mid1 = max(0, self.ep_mid2 - 1)
        # the list of poses for forward and backward walking
        self.walk_fw_sts, self.walk_bw_sts = [2, 3, 4, 5], [6, 5, 7, 3]
        # the list of poses for forward and backward skating
        self.skate_fw_sts, self.skate_bw_sts = [8, 9, 10, 11], [12, 1, 13, 9]
        # the list of safe poses for dancing
        self.dance_ok = [0, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13, 14, 16, 17]
        w_t, l_s, j_t = self.w_t, self.l_s, self.j_t
        # servo targets for each pose
        self.st_tg = [
            # stand
            [90, 90, 90, 90, 90, 80],
            # duck
            [10, 150, 170, 30, 40, 125],
            # 2, walk1
            [90 - w_t, 90 + 35, 90 - j_t, 90 + 30, 90 - l_s - 8, 80],
            # 3, w2
            [93, 90 + l_s, 93, 90 + l_s, 90 - l_s - 8, 80],
            # 4, w3
            [90 + j_t, 90 - 30, 90 + w_t, 90 - 35, 90 + l_s + 8, 80],
            # 5, w4
            [87, 90 - l_s, 87, 90 - l_s, 90 + l_s + 8, 80],
            # 6, w5
            [90 - w_t, 90 - 25, 90 - j_t, 90 - 45, 90 + l_s, 80],
            # 7, w6
            [90 + j_t, 90 + 45, 90 + w_t, 90 + 25, 90 - l_s, 80],
            # 8,skate 1
            [90 - w_t + 5, 90 + 35, 90 - w_t, 90 + 10, 90 + 35, 90 + 5],
            # s 2
            [90 + w_t - 5, 90 + 35, 90 + w_t - 5, 90 + 25, 90 - 20, 90 - 15],
            # s 3
            [90 + w_t, 90 - 10, 90 + w_t - 5, 90 - 35, 90 - 35, 90 + 5],
            # s4
            [90 - w_t + 5, 90 - 25, 90 - w_t + 5, 90 - 35, 90 + 20, 90 - 15],
            # s 5
            [90 - w_t + 5, 90 - 20, 90 - j_t, 90 - 20, 90 + 20, 90],
            # s 6
            [90 + j_t, 90 + 20, 90 + w_t - 5, 90 + 20, 90 - 20, 90],
            # 14,jump
            [130, 90, 50, 90, 90, 90],
            [0, 85, 180, 95, 90, 90],
            # 16 dance
            [85, 90, 95, 90, 45, 65],
            [85, 90, 95, 90, 135, 65],
            # 18 side move
            [75, 90, 30, 90, 135, 105],
            [150, 90, 105, 90, 45, 105],
            [75, 90, 30, 90, 45, 75],
            [150, 90, 105, 90, 135, 75],
            [75, 90, 75, 90, 90, 90],
            [105, 90, 105, 90, 90, 90],
            # 24 soccer
            [130, 90, 50, 90, 90, 55],
            # calibrate
            [90, 60, 90, 120, 90, 90],
            # rest
            [90, 90, 90, 90, 90, 90],
        ]
        # map servo target vector and control speed vector
        self.dict_sp = {
            0: 1,
            1: 0,
            2: 3,
            3: 4,
            4: 2,
            5: 4,
            6: 3,
            7: 2,
            8: 3,
            9: 4,
            10: 2,
            11: 4,
            12: 3,
            13: 2,
            14: 8,
            15: 10,
            16: 0,
            17: 0,
            18: 6,
            19: 6,
            20: 6,
            21: 6,
            22: 9,
            23: 7,
            24: 5,
            25: 7,
            26: 0
        }
        # servo control speed vectors  
        self.st_spu = [
            [1, 1, 1, 1, 1, 1], # 0 
            [1, 1, 1, 1, 0.5, 0.5], # 1
            [2, 1, 1, 1, 1.2, 0.4], # 2
            [1, 1, 2, 1, 1.2, 0.4], # 3
            [1, 1, 1, 1, 1.2, 0.4], # 4       
            [5, 1, 5, 1, 1, 5], # 5
            [0.55, 1, 0.55, 1, 1, 1], # 6
            [2, 1, 1, 1, 1, 1], # 7
            [5, 1, 5, 1, 1, 3], # 8
            [1, 1, 2, 1, 1, 1], # 9
            [6, 2, 6, 2, 1, 1] # 10
        ]