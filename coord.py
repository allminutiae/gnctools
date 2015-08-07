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
    def fromQuat(quat, scalarpos='first'):
        """
        Factory method to construct a Rotation object from a quaternion.

        :param quat:      quaternion; numpy.ndarray or other 4-element iterable
        :param scalarpos: 'first' or 'last'

        :return:
        """

        # validate input:
        if len(quat) != 4:
            raise ValueError('Argument must be a 4-element iterable of floats')
        for q in quat:
            if not isinstance(q, float):
                raise ValueError('Argument must be a 4-element iterable of floats')

        rot = Rotation()
        if scalarpos=='first':
            rot._qs = quat[0]
            rot._qx = quat[1]
            rot._qy = quat[2]
            rot._qz = quat[3]
        elif scalarpos=='last':
            rot._qs = quat[3]
            rot._qx = quat[0]
            rot._qy = quat[1]
            rot._qz = quat[2]

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

        Algorithm from NASA-TM-74839 "Euler Angles, Quaternions, and Transformation Matrices", page A-11
        """
        # TODO: add inference of units (e.g., if ang > 2*pi assume deg, else default to rad if not specified)

        s = np.sin
        c = np.cos

        z, y, x  = Rotation._in_radians(z/2, y/2, x/2, units)
        rot = Rotation()
        rot._qs =  s(x)*s(y)*s(z) + c(x)*c(y)*c(z)
        rot._qx = -s(x)*s(y)*c(z) + s(z)*c(x)*c(y)
        rot._qy =  s(x)*s(z)*c(y) + s(y)*c(x)*c(z)
        rot._qz =  s(x)*c(y)*c(z) - s(y)*s(z)*c(x)

        return rot

    @staticmethod
    def fromEulerYZX(y, z, x, units='rad'):
        """
        Factory method to construct Rotation object from euler angles.

        :param y:      y angle
        :param z:      z angle
        :param x:      x angle
        :param units:  'rad' or 'deg'

        :return:       Rotation object

        Algorithm from NASA-TM-74839 "Euler Angles, Quaternions, and Transformation Matrices", page A-7
        """

        s = np.sin
        c = np.cos

        z, y, x  = Rotation._in_radians(z/2, y/2, x/2, units)
        rot = Rotation()
        rot._qs = -s(x)*s(y)*s(z) + c(x)*c(y)*c(z)
        rot._qx =  s(x)*s(y)*c(z) + s(z)*c(x)*c(y)
        rot._qy =  s(x)*c(y)*c(z) + s(y)*s(z)*c(x)
        rot._qz = -s(x)*s(z)*c(y) + s(y)*c(x)*c(z)

        return rot

    @property
    def quat(self):
        return self._qs, self._qx, self._qy, self._qz

    def apply_to(self, other):
        """
        Applies this rotation to another rotation or a vector.

        :param   other: vector

        :return:

        NOTE: this is equivalent to the overloading of the multiplication operator (see __mul__() below)
        """



    @staticmethod
    def _in_radians(a, b, c, units):
        """

        :param a:
        :param b:
        :param c:
        :param units: 'deg' for deg, anything else assumes rad
        :return:      angles in radians
        """
        # TODO: add valueError for units not being 'rad' or 'deg'

        if units == 'deg':
            a *= Rotation.PIOVER180
            b *= Rotation.PIOVER180
            c *= Rotation.PIOVER180

        return a, b, c

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
        #TODO: add vector multiplication

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

