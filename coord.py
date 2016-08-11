import numpy as np

class Rotation:
    """
    Represents a coordinate system rotation in 3-space.

    """

    PIOVER180 = np.pi/180.

    """
    Member variables:
    _qs = float()
    _qx = float()
    _qy = float()
    _qz = float()
    """

    def __init__(self, *args, **kwargs):
        """

        :param   args:  if 1 arg, check to see if it's a quat or dcm (if quat and no kwarg['scalarpos']
                            assume scalar first)
                        if 3 args, should be euler angles (if no kwarg['eulerseq'] assume xyz)

        :param kwargs:  dcm       - 3x3 numpy.ndarray
                        quat      - 4-element array
                        scalarpos - 'first' or 'last'
                        eulerx    - x euler angle
                        eulery    - y euler angle
                        eulerz    - z euler angle
                        eulerseq  - euler sequence, ('xyz')
                        units     - 'deg' or 'rad'

        :return:        nothing
        """

        self._qs = float()
        self._qx = float()
        self._qy = float()
        self._qz = float()

    @staticmethod
    def fromQuat(quat,
                 scalarfirst: bool = True):
        """
        Factory method to construct a Rotation object from a quaternion.

        :param quat:        quaternion; numpy.ndarray or other 4-element iterable
        :param scalarfirst: denotes whether the scalar is first, if not, assumes last

        :return:
        """

        # validate input:
        if len(quat) != 4:
            raise ValueError('Argument must be a 4-element iterable of floats')
        for q in quat:
            if not isinstance(q, float):
                raise ValueError('Argument must be a 4-element iterable of floats')

        rot = Rotation()
        if scalarfirst:
            rot._qs = quat[0]
            rot._qx = quat[1]
            rot._qy = quat[2]
            rot._qz = quat[3]
        else:
            rot._qs = quat[3]
            rot._qx = quat[0]
            rot._qy = quat[1]
            rot._qz = quat[2]

        rot._normalize()
        return rot

    @staticmethod
    def fromEulerZYX(z, y, x, units='rad'):
        """
        Factory method to construct Rotation object from euler angles.

        :param z:      z angle
        :param y:      y angle
        :param x:      x angle
        :param units:  'rad' or 'deg'

        :return:       Rotation object

        """
        # TODO: add inference of units (e.g., if ang > 2*pi assume deg, else default to rad if not specified)

        s = np.sin
        c = np.cos

        z, y, x  = Rotation._in_radians((z/2, y/2, x/2), units)
        rot = Rotation()
        rot._qs = c(x)*c(y)*c(z) + s(x)*s(y)*s(z)
        rot._qx = s(x)*c(y)*c(z) - c(x)*s(y)*s(z)
        rot._qy = c(x)*s(y)*c(z) + s(x)*c(y)*s(z)
        rot._qz = c(x)*c(y)*s(z) - s(x)*s(y)*c(z)

        return rot

    @property
    def quat(self):
        """
        Returns the quaternion representing this rotation.
        """
        return np.array((self._qs, self._qx, self._qy, self._qz))

    @property
    def quat_conj(self):
        """
        Returns the conjugate quaternion.
        """
        return self.quat * np.array((1, -1, -1, -1))

    @property
    def dcm(self):
        """
        Returns the DCM representing the rotation.

        :return: a numpy.ndarray
        """

        d = self._qs
        a = self._qx
        b = self._qy
        c = self._qz

        dd = d * d
        aa = a * a
        bb = b * b
        cc = c * c
        ab = a * b
        ac = a * c
        ad = a * d
        bc = b * c
        bd = b * d
        cd = c * d

        dcm = np.empty((3,3))
        dcm[0, 0] = dd + aa - bb - cc
        dcm[0, 1] = 2.0 * ( cd + ab)
        dcm[0, 2] = 2.0 * ( ac - bd)
        dcm[1, 0] = 2.0 * ( ab - cd)
        dcm[1, 1] = dd - aa + bb - cc
        dcm[1, 2] = 2.0 * ( ad + bc)
        dcm[2, 0] = 2.0 * ( bd + ac)
        dcm[2, 1] = 2.0 * ( bc - ad)
        dcm[2, 2] = dd - aa - bb + cc

        return dcm

    @property
    def eulerZYX(self):
        """
        Returns the equivalent Yaw, Pitch, Roll Euler sequence, in radians.

        :return: a tuple
        """

        qs, q1, q2, q3 = self.quat
        roll  = np.arctan2(2 * (qs * q1 + q2 * q3), 1 - 2 * (q1**2 - q2**2))
        pitch = np.arcsin(2 * (qs * q2 - q3 * q1))
        yaw   = np.arctan2(2 * (qs * q3 + q1 * q2), 1 - 2 * (q2**2 + q3**2))

        return yaw, pitch, roll

    def angular_diff(self, rot):
        """
        Calculates the angle of rotation required to get from the orientation encapsulated herein to the
        given Rotation object.

        :param   rot: the other rotation object

        :return: angular difference, in radians

        Algorithm is for the geodesic distance between the normed quaternions, from "Metrics for 3D Rotations:
        Comparison and Analysis"--Huynh
        """

        qprod = self.quat*rot.quat

        return np.arccos(2*np.sum(qprod)**2 - 1)

    @property
    def inverse(self):
        """
        Returns the inverse of this rotation.
        """

        d = sum(self.quat**2)

        return Rotation.fromQuat(self.quat_conj / d)

    def _normalize(self):
        """
        Normalizes the internal quaternion.

        :return: Nothing.
        """

        q = self.quat
        self._qs, self._qx, self._qy, self._qz = q/np.linalg.norm(q)

    @staticmethod
    def _in_radians(ang, units):
        """
        Just converts angles to radians.

        :param ang:   an iterable of angles or a single angle
        :param units: 'deg' for deg, anything else assumes rad
        :return:      angles in radians
        """
        # TODO: add valueError for units not being 'rad' or 'deg'

        if units == 'deg':
            if hasattr(ang, '__iter__'):
                ang = tuple(a * Rotation.PIOVER180 for a in ang)
            else:
                ang *= Rotation.PIOVER180

        return ang

    @staticmethod
    def __mult_quat_quat(q1, q2):
        """
        Assumes scalar is first element
        """

        a_s = q1[0] * q2[0] - q1[1] * q2[1] - q1[2] * q2[2] - q1[3] * q2[3]
        a_1 = q1[0] * q2[1] + q1[1] * q2[0] + q1[2] * q2[3] - q1[3] * q2[2]
        a_2 = q1[0] * q2[2] - q1[1] * q2[3] + q1[2] * q2[0] + q1[3] * q2[1]
        a_3 = q1[0] * q2[3] + q1[1] * q2[2] - q1[2] * q2[1] + q1[3] * q2[0]

        return a_s, a_1, a_2, a_3

    @staticmethod
    def __mult_quat_vec(q, v):
        """
        Rotates a vector according to provided quaternion.

        :param   q: Quaternion.  Assumes scalar first element.
        :param   v: Vector.  Iterable of length 3.

        :return: Rotated vector as tuple.
        """

        w1 = q[3] * v[1] - q[2] * v[2]
        w2 = q[1] * v[2] - q[3] * v[0]
        w3 = q[2] * v[0] - q[1] * v[1]

        x = v[0] + 2. * (q[0] * w1 - q[2] * w3 + q[3] * w2)
        y = v[1] + 2. * (q[0] * w2 - q[3] * w1 + q[1] * w3)
        z = v[2] + 2. * (q[0] * w3 - q[1] * w2 + q[2] * w1)

        return x, y, z

    #TODO: add __check_type and __sanitize_type methods (static) to sanitize inputs, centralize this
    #      job so other methods can use the same code to do this job.

    def __mul__(self,
                other: 'iterable of length 3 (vector) or another rotation'):
        """
        Overloads the * operator.  Applies the rotation to a vector or other rotation;
        returns the result of the rotation.

        :param      other: 3-space vector-like (tuple/list/numpy.ndarray), or
                           other Rotation object

        :return:    the resulting rotated vector
        """

        if isinstance(other, self.__class__):
            # rotate a rotation
            return Rotation.fromQuat(Rotation.__mult_quat_quat(self.quat, other.quat))
        elif hasattr(other, '__iter__') and len(other) == 3 and isinstance(other[0], float):
            # rotate a vector
            return Rotation.__mult_quat_vec(self.quat, other)
        else:
            # don't know what that is
            raise TypeError('Operand only supported for operations between 2 Rotation objects or \
                             by 1 Rotation object and a 3-element iterable')

