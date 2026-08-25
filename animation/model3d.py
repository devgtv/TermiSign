import math
from OpenGL.GL import *
from OpenGL.GLU import *


def draw_sphere(radius, slices=16, stacks=12):
    quad = gluNewQuadric()
    gluQuadricNormals(quad, GLU_SMOOTH)
    gluSphere(quad, radius, slices, stacks)
    gluDeleteQuadric(quad)


def draw_cylinder(radius, height, slices=12):
    quad = gluNewQuadric()
    gluQuadricNormals(quad, GLU_SMOOTH)
    glPushMatrix()
    glRotatef(-90, 1, 0, 0)
    gluCylinder(quad, radius, radius, height, slices, 1)
    glPopMatrix()
    gluDeleteQuadric(quad)


def draw_tapered_cylinder(base_r, top_r, height, slices=12):
    quad = gluNewQuadric()
    gluQuadricNormals(quad, GLU_SMOOTH)
    glPushMatrix()
    glRotatef(-90, 1, 0, 0)
    gluCylinder(quad, base_r, top_r, height, slices, 1)
    glPopMatrix()
    gluDeleteQuadric(quad)


def draw_sphere_at(x, y, z, radius, color):
    glPushMatrix()
    glTranslatef(x, y, z)
    glColor3f(*color)
    draw_sphere(radius)
    glPopMatrix()


def draw_capsule(x, y, z, radius, height, angle_x=0, angle_y=0, angle_z=0, color=(0.3, 0.6, 0.9)):
    glPushMatrix()
    glTranslatef(x, y, z)
    glRotatef(angle_x, 1, 0, 0)
    glRotatef(angle_y, 0, 1, 0)
    glRotatef(angle_z, 0, 0, 1)
    glColor3f(*color)

    half_h = height / 2.0
    draw_cylinder(radius, height)

    glPushMatrix()
    glTranslatef(0, half_h, 0)
    draw_sphere(radius)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(0, -half_h, 0)
    draw_sphere(radius)
    glPopMatrix()

    glPopMatrix()


SKIN = (0.92, 0.75, 0.55)
SHIRT = (0.2, 0.5, 0.8)
PANTS = (0.25, 0.25, 0.45)
SHOE = (0.2, 0.15, 0.1)


class HumanoidModel:
    def __init__(self):
        self.head_y = 3.6
        self.torso_y = 2.5
        self.hip_y = 1.6
        self.shoulder_y = 3.1
        self.hand_y = 1.8

        self.left_shoulder_angle = 0
        self.left_elbow_angle = 0
        self.left_wrist_angle = 0
        self.right_shoulder_angle = 0
        self.right_elbow_angle = 0
        self.right_wrist_angle = 0

        self.finger_spread = 0.0
        self.thumb_out = 0.0
        self.index_up = 0.0
        self.middle_up = 0.0
        self.ring_up = 0.0
        self.pinky_up = 0.0
        self.index_hook = 0.0

    def set_pose(self, pose_name: str):
        poses = POSE_3D_MAP.get(pose_name, POSE_3D_MAP["idle"])
        for key, val in poses.items():
            if hasattr(self, key):
                setattr(self, key, val)

    def draw(self):
        self._draw_head()
        self._draw_torso()
        self._draw_legs()
        self._draw_left_arm()
        self._draw_right_arm()

    def _draw_head(self):
        glPushMatrix()
        glTranslatef(0, self.head_y, 0)
        glColor3f(*SKIN)
        draw_sphere(0.4, 20, 16)

        glColor3f(0.15, 0.15, 0.15)
        draw_sphere_at(-0.12, 0.08, 0.35, 0.05, (0.1, 0.1, 0.1))
        draw_sphere_at(0.12, 0.08, 0.35, 0.05, (0.1, 0.1, 0.1))

        glColor3f(0.7, 0.35, 0.35)
        draw_sphere_at(0, -0.05, 0.42, 0.06, (0.75, 0.4, 0.4))

        glPushMatrix()
        glTranslatef(-0.25, 0.35, 0.0)
        glRotatef(-20, 0, 0, 1)
        draw_cylinder(0.06, 0.25)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(0.25, 0.35, 0.0)
        glRotatef(20, 0, 0, 1)
        draw_cylinder(0.06, 0.25)
        glPopMatrix()

        glPopMatrix()

    def _draw_torso(self):
        glColor3f(*SHIRT)
        draw_tapered_cylinder(0.45, 0.35, 1.6)

        glPushMatrix()
        glTranslatef(0, 0.8, 0)
        draw_sphere(0.48)
        glPopMatrix()

    def _draw_legs(self):
        leg_spread = 0.2

        glPushMatrix()
        glTranslatef(-leg_spread, -0.3, 0)
        glColor3f(*PANTS)
        draw_capsule(0, 0, 0, 0.15, 1.0, color=PANTS)
        glTranslatef(0, -0.5, 0)
        draw_capsule(0, 0, 0, 0.13, 0.9, color=PANTS)
        glTranslatef(0, -0.5, 0.1)
        glColor3f(*SHOE)
        draw_tapered_cylinder(0.14, 0.12, 0.35)
        glTranslatef(0, -0.1, 0.1)
        draw_sphere(0.13)
        glPopMatrix()

        glPushMatrix()
        glTranslatef(leg_spread, -0.3, 0)
        glColor3f(*PANTS)
        draw_capsule(0, 0, 0, 0.15, 1.0, color=PANTS)
        glTranslatef(0, -0.5, 0)
        draw_capsule(0, 0, 0, 0.13, 0.9, color=PANTS)
        glTranslatef(0, -0.5, 0.1)
        glColor3f(*SHOE)
        draw_tapered_cylinder(0.14, 0.12, 0.35)
        glTranslatef(0, -0.1, 0.1)
        draw_sphere(0.13)
        glPopMatrix()

    def _draw_arm(self, side=1):
        sx = side * 0.55
        glPushMatrix()
        glTranslatef(sx, self.shoulder_y, 0)
        glRotatef(side * self.left_shoulder_angle if side < 0 else side * self.right_shoulder_angle, 0, 0, 1)
        glColor3f(*SHIRT)
        draw_capsule(0, 0, 0, 0.12, 0.5, color=SHIRT)

        glTranslatef(0, -0.35, 0)
        glColor3f(*SKIN)
        draw_capsule(0, 0, 0, 0.1, 0.45, color=SKIN)

        glTranslatef(0, -0.3, 0)
        glRotatef(self.left_elbow_angle if side < 0 else self.right_elbow_angle, 1, 0, 0)
        draw_capsule(0, 0, 0, 0.09, 0.4, color=SKIN)

        glTranslatef(0, -0.28, 0)
        self._draw_hand(side)

        glPopMatrix()

    def _draw_left_arm(self):
        self._draw_arm(-1)

    def _draw_right_arm(self):
        self._draw_arm(1)

    def _draw_hand(self, side=1):
        glPushMatrix()
        glRotatef(self.left_wrist_angle if side < 0 else self.right_wrist_angle, 1, 0, 0)

        glColor3f(*SKIN)
        draw_sphere(0.08)

        finger_len = 0.12
        thumb_len = 0.1
        spread = 0.04 + self.finger_spread * 0.03

        base_x = [-spread * 1.5, -spread * 0.5, spread * 0.5, spread * 1.5]
        base_up = [self.index_up, self.middle_up, self.ring_up, self.pinky_up]
        hook = [self.index_hook, 0, 0, 0]

        for i in range(4):
            glPushMatrix()
            glTranslatef(base_x[i], -0.08, 0)
            glRotatef(hook[i] * 45, 1, 0, 0)
            glColor3f(*SKIN)
            draw_capsule(0, 0, 0, 0.025, finger_len, color=SKIN)

            tip_up = base_up[i] * 0.06
            glTranslatef(0, -finger_len * 0.5, tip_up)
            draw_capsule(0, 0, 0, 0.02, finger_len * 0.6, color=SKIN)
            glPopMatrix()

        glPushMatrix()
        thumb_x = -0.12 if side < 0 else 0.12
        glTranslatef(thumb_x, -0.02, self.thumb_out * 0.08)
        glRotatef(-30 * side, 0, 0, 1)
        glColor3f(*SKIN)
        draw_capsule(0, 0, 0, 0.028, thumb_len, color=SKIN)
        glTranslatef(0, -thumb_len * 0.5, 0)
        draw_capsule(0, 0, 0, 0.022, thumb_len * 0.6, color=SKIN)
        glPopMatrix()

        glPopMatrix()


POSE_3D_MAP = {
    "idle": {
        "left_shoulder_angle": 15,
        "left_elbow_angle": -10,
        "right_shoulder_angle": -15,
        "right_elbow_angle": -10,
        "finger_spread": 0.3,
        "thumb_out": 0.5,
        "index_up": 0.3,
        "middle_up": 0.3,
        "ring_up": 0.3,
        "pinky_up": 0.3,
        "index_hook": 0,
    },
    "fist_thumb_side": {
        "right_shoulder_angle": -45,
        "right_elbow_angle": -60,
        "right_wrist_angle": 0,
        "finger_spread": 0,
        "thumb_out": 1.0,
        "index_up": 0,
        "middle_up": 0,
        "ring_up": 0,
        "pinky_up": 0,
        "index_hook": 0,
    },
    "flat_palm": {
        "right_shoulder_angle": -45,
        "right_elbow_angle": -60,
        "finger_spread": 0.2,
        "thumb_out": 0.3,
        "index_up": 1.0,
        "middle_up": 1.0,
        "ring_up": 1.0,
        "pinky_up": 1.0,
        "index_hook": 0,
    },
    "c_curve": {
        "right_shoulder_angle": -45,
        "right_elbow_angle": -60,
        "right_wrist_angle": -20,
        "finger_spread": 0.3,
        "thumb_out": 0.5,
        "index_up": 0.7,
        "middle_up": 0.7,
        "ring_up": 0.7,
        "pinky_up": 0.7,
        "index_hook": 0.3,
    },
    "index_up_circle": {
        "right_shoulder_angle": -45,
        "right_elbow_angle": -60,
        "finger_spread": 0,
        "thumb_out": 0.8,
        "index_up": 1.0,
        "middle_up": 0,
        "ring_up": 0,
        "pinky_up": 0,
        "index_hook": 0,
    },
    "claw_closed": {
        "right_shoulder_angle": -45,
        "right_elbow_angle": -60,
        "finger_spread": 0.1,
        "thumb_out": 0.2,
        "index_up": 0.3,
        "middle_up": 0.3,
        "ring_up": 0.3,
        "pinky_up": 0.3,
        "index_hook": 0.6,
    },
    "ok_outside": {
        "right_shoulder_angle": -45,
        "right_elbow_angle": -60,
        "finger_spread": 0.5,
        "thumb_out": 0.9,
        "index_up": 1.0,
        "middle_up": 1.0,
        "ring_up": 1.0,
        "pinky_up": 1.0,
        "index_hook": 0,
    },
    "pinch_up": {
        "right_shoulder_angle": -45,
        "right_elbow_angle": -60,
        "finger_spread": 0.1,
        "thumb_out": 0.9,
        "index_up": 1.0,
        "middle_up": 0,
        "ring_up": 0,
        "pinky_up": 0,
        "index_hook": 0,
    },
    "two_fingers_horizontal": {
        "right_shoulder_angle": -30,
        "right_elbow_angle": -90,
        "right_wrist_angle": -90,
        "finger_spread": 0.3,
        "thumb_out": 0.5,
        "index_up": 1.0,
        "middle_up": 1.0,
        "ring_up": 0,
        "pinky_up": 0,
        "index_hook": 0,
    },
    "pinky_up": {
        "right_shoulder_angle": -45,
        "right_elbow_angle": -60,
        "finger_spread": 0,
        "thumb_out": 0.2,
        "index_up": 0,
        "middle_up": 0,
        "ring_up": 0,
        "pinky_up": 1.0,
        "index_hook": 0,
    },
    "pinky_hook": {
        "right_shoulder_angle": -45,
        "right_elbow_angle": -60,
        "finger_spread": 0,
        "thumb_out": 0.2,
        "index_up": 0,
        "middle_up": 0,
        "ring_up": 0,
        "pinky_up": 0.7,
        "index_hook": 0,
    },
    "two_fingers_up": {
        "right_shoulder_angle": -45,
        "right_elbow_angle": -60,
        "finger_spread": 0.1,
        "thumb_out": 0.3,
        "index_up": 1.0,
        "middle_up": 1.0,
        "ring_up": 0,
        "pinky_up": 0,
        "index_hook": 0,
    },
    "l_shape": {
        "right_shoulder_angle": -45,
        "right_elbow_angle": -90,
        "finger_spread": 0,
        "thumb_out": 1.0,
        "index_up": 1.0,
        "middle_up": 0,
        "ring_up": 0,
        "pinky_up": 0,
        "index_hook": 0,
    },
    "three_over_thumb": {
        "right_shoulder_angle": -45,
        "right_elbow_angle": -60,
        "finger_spread": 0.2,
        "thumb_out": 0.1,
        "index_up": 0.1,
        "middle_up": 0.1,
        "ring_up": 0.1,
        "pinky_up": 0,
        "index_hook": 0,
    },
    "two_over_thumb": {
        "right_shoulder_angle": -45,
        "right_elbow_angle": -60,
        "finger_spread": 0.1,
        "thumb_out": 0.1,
        "index_up": 0.1,
        "middle_up": 0.1,
        "ring_up": 0,
        "pinky_up": 0,
        "index_hook": 0,
    },
    "circle": {
        "right_shoulder_angle": -45,
        "right_elbow_angle": -60,
        "right_wrist_angle": -10,
        "finger_spread": 0.2,
        "thumb_out": 0.7,
        "index_up": 0.5,
        "middle_up": 0.5,
        "ring_up": 0.5,
        "pinky_up": 0.5,
        "index_hook": 0.3,
    },
    "two_fingers_down": {
        "right_shoulder_angle": -45,
        "right_elbow_angle": -60,
        "right_wrist_angle": 40,
        "finger_spread": 0.1,
        "thumb_out": 0.3,
        "index_up": 1.0,
        "middle_up": 1.0,
        "ring_up": 0,
        "pinky_up": 0,
        "index_hook": 0,
    },
    "pinch_down": {
        "right_shoulder_angle": -45,
        "right_elbow_angle": -60,
        "right_wrist_angle": 30,
        "finger_spread": 0.1,
        "thumb_out": 0.9,
        "index_up": 1.0,
        "middle_up": 0,
        "ring_up": 0,
        "pinky_up": 0,
        "index_hook": 0,
    },
    "crossed_fingers": {
        "right_shoulder_angle": -45,
        "right_elbow_angle": -60,
        "finger_spread": 0,
        "thumb_out": 0.2,
        "index_up": 1.0,
        "middle_up": 1.0,
        "ring_up": 0,
        "pinky_up": 0,
        "index_hook": 0,
    },
    "fist_thumb_front": {
        "right_shoulder_angle": -45,
        "right_elbow_angle": -60,
        "finger_spread": 0,
        "thumb_out": 0.5,
        "index_up": 0,
        "middle_up": 0,
        "ring_up": 0,
        "pinky_up": 0,
        "index_hook": 0,
    },
    "thumb_inside": {
        "right_shoulder_angle": -45,
        "right_elbow_angle": -60,
        "finger_spread": 0.1,
        "thumb_out": 0.0,
        "index_up": 0.1,
        "middle_up": 0.1,
        "ring_up": 0.1,
        "pinky_up": 0,
        "index_hook": 0,
    },
    "two_fingers_together": {
        "right_shoulder_angle": -45,
        "right_elbow_angle": -60,
        "finger_spread": 0,
        "thumb_out": 0.2,
        "index_up": 1.0,
        "middle_up": 1.0,
        "ring_up": 0,
        "pinky_up": 0,
        "index_hook": 0,
    },
    "v_shape": {
        "right_shoulder_angle": -45,
        "right_elbow_angle": -60,
        "finger_spread": 0.5,
        "thumb_out": 0.3,
        "index_up": 1.0,
        "middle_up": 1.0,
        "ring_up": 0,
        "pinky_up": 0,
        "index_hook": 0,
    },
    "three_fingers_spread": {
        "right_shoulder_angle": -45,
        "right_elbow_angle": -60,
        "finger_spread": 0.6,
        "thumb_out": 0.2,
        "index_up": 1.0,
        "middle_up": 1.0,
        "ring_up": 1.0,
        "pinky_up": 0,
        "index_hook": 0,
    },
    "hook_index": {
        "right_shoulder_angle": -45,
        "right_elbow_angle": -60,
        "finger_spread": 0,
        "thumb_out": 0.3,
        "index_up": 0.3,
        "middle_up": 0,
        "ring_up": 0,
        "pinky_up": 0,
        "index_hook": 0.8,
    },
    "shaka": {
        "right_shoulder_angle": -45,
        "right_elbow_angle": -60,
        "finger_spread": 0.5,
        "thumb_out": 1.0,
        "index_up": 0,
        "middle_up": 0,
        "ring_up": 0,
        "pinky_up": 1.0,
        "index_hook": 0,
    },
    "index_trace": {
        "right_shoulder_angle": -45,
        "right_elbow_angle": -60,
        "finger_spread": 0,
        "thumb_out": 0.3,
        "index_up": 1.0,
        "middle_up": 0,
        "ring_up": 0,
        "pinky_up": 0,
        "index_hook": 0.2,
    },
    "zero_sphere": {
        "right_shoulder_angle": -45,
        "right_elbow_angle": -60,
        "finger_spread": 0.2,
        "thumb_out": 0.7,
        "index_up": 0.5,
        "middle_up": 0.5,
        "ring_up": 0.5,
        "pinky_up": 0.5,
        "index_hook": 0.3,
    },
    "one_index": {
        "right_shoulder_angle": -45,
        "right_elbow_angle": -60,
        "finger_spread": 0,
        "thumb_out": 0.2,
        "index_up": 1.0,
        "middle_up": 0,
        "ring_up": 0,
        "pinky_up": 0,
        "index_hook": 0,
    },
    "two_v": {
        "right_shoulder_angle": -45,
        "right_elbow_angle": -60,
        "finger_spread": 0.5,
        "thumb_out": 0.3,
        "index_up": 1.0,
        "middle_up": 1.0,
        "ring_up": 0,
        "pinky_up": 0,
        "index_hook": 0,
    },
    "three_thumb_v": {
        "right_shoulder_angle": -45,
        "right_elbow_angle": -60,
        "finger_spread": 0.4,
        "thumb_out": 1.0,
        "index_up": 1.0,
        "middle_up": 1.0,
        "ring_up": 0,
        "pinky_up": 0,
        "index_hook": 0,
    },
    "four_fingers": {
        "right_shoulder_angle": -45,
        "right_elbow_angle": -60,
        "finger_spread": 0.3,
        "thumb_out": 0.1,
        "index_up": 1.0,
        "middle_up": 1.0,
        "ring_up": 1.0,
        "pinky_up": 1.0,
        "index_hook": 0,
    },
    "five_open": {
        "right_shoulder_angle": -45,
        "right_elbow_angle": -60,
        "finger_spread": 0.6,
        "thumb_out": 1.0,
        "index_up": 1.0,
        "middle_up": 1.0,
        "ring_up": 1.0,
        "pinky_up": 1.0,
        "index_hook": 0,
    },
    "six_thumb_index": {
        "right_shoulder_angle": -45,
        "right_elbow_angle": -60,
        "finger_spread": 0.3,
        "thumb_out": 0.5,
        "index_up": 0.6,
        "middle_up": 1.0,
        "ring_up": 1.0,
        "pinky_up": 1.0,
        "index_hook": 0,
    },
    "seven_thumb_ring": {
        "right_shoulder_angle": -45,
        "right_elbow_angle": -60,
        "finger_spread": 0.3,
        "thumb_out": 0.5,
        "index_up": 1.0,
        "middle_up": 1.0,
        "ring_up": 0.6,
        "pinky_up": 1.0,
        "index_hook": 0,
    },
    "eight_thumb_middle": {
        "right_shoulder_angle": -45,
        "right_elbow_angle": -60,
        "finger_spread": 0.3,
        "thumb_out": 0.5,
        "index_up": 1.0,
        "middle_up": 0.6,
        "ring_up": 1.0,
        "pinky_up": 1.0,
        "index_hook": 0,
    },
    "nine_thumb_index_in": {
        "right_shoulder_angle": -45,
        "right_elbow_angle": -60,
        "finger_spread": 0.3,
        "thumb_out": 0.5,
        "index_up": 0.6,
        "middle_up": 1.0,
        "ring_up": 1.0,
        "pinky_up": 1.0,
        "index_hook": 0,
    },
}
