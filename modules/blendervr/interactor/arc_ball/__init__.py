import copy
import math

# //assuming IEEE-754(GLfloat), which i believe has max precision of 7 bits
Epsilon = 1.0e-5

from .. import Interactor

class ArcBall(Interactor):

    def __init__ (self, parent, NewWidth, NewHeight):
        Interactor.__init__ (self, parent)
        self.m_StVec = (0.0, 0.0)
        self.m_EnVec = (0.0, 0.0)
        self.m_AdjustWidth = 1.0
        self.m_AdjustHeight = 1.0
        self.setBounds (NewWidth, NewHeight)
        self.setOrientation(True)

    def setOrientation(self, direct):
        self._direct = direct

    def __str__ (self):
        str_rep = ""
        str_rep += "StVec = " + str (self.m_StVec)
        str_rep += "\nEnVec = " + str (self.m_EnVec)
        str_rep += "\n scale coords %f %f" % (self.m_AdjustWidth, self.m_AdjustHeight)
        return str_rep

    def setBounds (self, NewWidth, NewHeight):
         # //Set new bounds
        assert (NewWidth > 1.0 and NewHeight > 1.0), "Invalid width or height for bounds."
        # //Set adjustment factor for width/height
        self.m_AdjustWidth = 2.0 / NewWidth
        self.m_AdjustHeight = 2.0 / NewHeight

    def _mapToSphere (self, mouse_position):
        X = 0
        Y = 1
        Z = 2

        planar_vector = ((mouse_position [X] * self.m_AdjustWidth) - 1.0, 1.0 - (mouse_position [Y] * self.m_AdjustHeight))

        length_square = planar_vector[X] * planar_vector[X] + planar_vector[Y] * planar_vector[Y]

        spatial_vector = [0.0, 0.0, 0.0]
        if (length_square > 1.0):
            spatial_vector[X] = planar_vector [X] / math.sqrt (length_square)
            spatial_vector[Y] = planar_vector [Y] / math.sqrt (length_square)
        else:
            spatial_vector[X] = planar_vector [X]
            spatial_vector[Y] = planar_vector [Y]
            spatial_vector[Z] = math.sqrt (1.0 - length_square)
            if not self._direct:
                spatial_vector[Z] *= -1.0

        return spatial_vector

    def click (self, mouse_position):
        self.m_StVec = self._mapToSphere (mouse_position)

    def drag (self, mouse_position):
        """ drag (Point2fT mouse_coord) -> new_quaternion_rotation_vec
        """
        X = 0
        Y = 1
        Z = 2
        W = 3

        self.m_EnVec   = self._mapToSphere (mouse_position)

        # Cross product !
        rotation_axis  = [self.m_StVec[1] * self.m_EnVec[2] - self.m_StVec[2] * self.m_EnVec[1],
                  self.m_StVec[2] * self.m_EnVec[0] - self.m_StVec[0] * self.m_EnVec[2],
                  self.m_StVec[0] * self.m_EnVec[1] - self.m_StVec[1] * self.m_EnVec[0]]

        

        axis_length = math.sqrt(rotation_axis[0] * rotation_axis[0] +
                    rotation_axis[1] * rotation_axis[1] +
                    rotation_axis[2] * rotation_axis[2])

        if axis_length > Epsilon:
            matrix = [[0.0, 0.0, 0.0],
                  [0.0, 0.0, 0.0],
                  [0.0, 0.0, 0.0]]

            rotation_axis[0] = rotation_axis[0] / axis_length
            rotation_axis[1] = rotation_axis[1] / axis_length
            rotation_axis[2] = rotation_axis[2] / axis_length

            rotation_angle = math.acos(self.m_StVec[0] * self.m_EnVec[0] +
                           self.m_StVec[1] * self.m_EnVec[1] +
                           self.m_StVec[2] * self.m_EnVec[2])

            cos = math.cos(rotation_angle)
            sin = math.sin(rotation_angle)
            _cos = 1 - cos

            matrix [X][X] = cos + rotation_axis[X] * rotation_axis[X] * _cos
            matrix [Y][Y] = cos + rotation_axis[Y] * rotation_axis[Y] * _cos
            matrix [Z][Z] = cos + rotation_axis[Z] * rotation_axis[Z] * _cos

            matrix [Y][X] = rotation_axis[X] * rotation_axis[Y] * _cos - rotation_axis[Z] * sin
            matrix [X][Y] = rotation_axis[Y] * rotation_axis[X] * _cos + rotation_axis[Z] * sin

            matrix [Z][X] = rotation_axis[X] * rotation_axis[Z] * _cos + rotation_axis[Y] * sin
            matrix [X][Z] = rotation_axis[Z] * rotation_axis[X] * _cos - rotation_axis[Y] * sin

            matrix [Z][Y] = rotation_axis[Y] * rotation_axis[Z] * _cos - rotation_axis[X] * sin
            matrix [Y][Z] = rotation_axis[Z] * rotation_axis[Y] * _cos + rotation_axis[X] * sin

            return matrix

        return [[1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0]]

    def getMatrixFromQuaternion(quaternion):
        # Converts the H quaternion quaternion into a new equivalent 3x3 rotation matrix. 
        X = 0
        Y = 1
        Z = 2
        W = 3

        norme = quaternion[0] * quaternion[0] + quaternion[1] * quaternion[1] + quaternion[2] * quaternion[2]

        s = 0.0
        if (norme > 0.0):
            s = 2.0 / norme
        xs = quaternion [X] * s;  ys = quaternion [Y] * s;  zs = quaternion [Z] * s
        wx = quaternion [W] * xs; wy = quaternion [W] * ys; wz = quaternion [W] * zs
        xx = quaternion [X] * xs; xy = quaternion [X] * ys; xz = quaternion [X] * zs
        yy = quaternion [Y] * ys; yz = quaternion [Y] * zs; zz = quaternion [Z] * zs

        matrix = [[0.0, 0.0, 0.0],
              [0.0, 0.0, 0.0],
              [0.0, 0.0, 0.0]]
        matrix [X][X] = 1.0 - (yy + zz); matrix [Y][X] =        xy - wz ; matrix [Z][X] =        xz + wy;
        matrix [X][Y] =        xy + wz ; matrix [Y][Y] = 1.0 - (xx + zz); matrix [Z][Y] =        yz - wx;
        matrix [X][Z] =        xz - wy ; matrix [Y][Z] =        yz + wx ; matrix [Z][Z] = 1.0 - (xx + yy)

        return matrix

def removeScale(matrix):
    destination = [matrix[0][0] + matrix[1][0] + matrix[2][0],
               matrix[0][1] + matrix[1][1] + matrix[2][1],
               matrix[0][2] + matrix[1][2] + matrix[2][2]]

    scale = math.sqrt(3) / math.sqrt(destination[0] * destination[0] + destination[1] * destination[1] + destination[2] * destination[2])
    if scale != 1.0:
        matrix[0][0] *= scale
        matrix[1][1] *= scale
        matrix[2][2] *= scale
    return matrix
