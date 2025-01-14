import numpy as np
import zivid
import zivid.calibration
from scipy.spatial.transform import Rotation as R

from zivid_nova.models.pose import Pose


def test_from_matrix():
    # Create a known transformation matrix
    position = np.array([1.0, 2.0, 3.0])
    rotation_vector = np.array([0.1, 0.2, 0.3])
    rotation_matrix = R.from_rotvec(rotation_vector).as_matrix()
    matrix = np.eye(4)
    matrix[:3, :3] = rotation_matrix
    matrix[:3, 3] = position

    # Create Pose from matrix
    pose = Pose.from_matrix(matrix)

    # Verify position and orientation
    np.testing.assert_array_almost_equal(pose.position, position)
    np.testing.assert_array_almost_equal(pose.orientation, rotation_vector)


def test_to_matrix():
    # Define position and orientation
    position = (1.0, 2.0, 3.0)
    orientation = (0.1, 0.2, 0.3)

    # Create Pose instance
    pose = Pose(position=position, orientation=orientation)

    # Convert to matrix
    matrix = pose.to_matrix()

    # Expected matrix
    expected_rotation = R.from_rotvec(orientation).as_matrix()
    expected_matrix = np.eye(4)
    expected_matrix[:3, :3] = expected_rotation
    expected_matrix[:3, 3] = position

    # Verify the matrix
    np.testing.assert_array_almost_equal(matrix, expected_matrix)


def test_round_trip_conversion():
    # Random position and orientation
    position = np.random.rand(3)
    orientation = np.random.rand(3)

    # Create Pose instance
    pose = Pose(position=tuple(position), orientation=tuple(orientation))

    # Convert to matrix and back
    matrix = pose.to_matrix()
    new_pose = Pose.from_matrix(matrix)

    # Verify that the new pose matches the original
    np.testing.assert_array_almost_equal(new_pose.position, position)
    np.testing.assert_array_almost_equal(new_pose.orientation, orientation)


def test_from_zivid_pose():
    # Create a known transformation matrix
    position = np.array([1.0, 2.0, 3.0])
    rotation_vector = np.array([0.1, 0.2, 0.3])
    rotation_matrix = R.from_rotvec(rotation_vector).as_matrix()
    matrix = np.eye(4)
    matrix[:3, :3] = rotation_matrix
    matrix[:3, 3] = position

    # Create a Zivid pose
    zivid_pose = zivid.calibration.Pose(matrix)

    # Convert to Pose
    pose = Pose.from_zivid_pose(zivid_pose)

    # Verify position and orientation
    np.testing.assert_array_almost_equal(pose.position, position)
    np.testing.assert_array_almost_equal(pose.orientation, rotation_vector)


def test_to_zivid_pose():
    # Define position and orientation
    position = (1.0, 2.0, 3.0)
    orientation = (0.1, 0.2, 0.3)

    # Create Pose instance
    pose = Pose(position=position, orientation=orientation)

    # Convert to Zivid pose
    zivid_pose = pose.to_zivid_pose()

    # Verify the Zivid pose
    np.testing.assert_array_almost_equal(zivid_pose.to_matrix(), pose.to_matrix())


def test_to_zivid_pose_round_trip():
    # Random position and orientation
    position = np.random.rand(3)
    orientation = np.random.rand(3)

    # Create Pose instance
    pose = Pose(position=tuple(position), orientation=tuple(orientation))

    # Convert to Zivid pose and back
    zivid_pose = pose.to_zivid_pose()
    new_pose = Pose.from_zivid_pose(zivid_pose)

    # Verify that the new pose matches the original
    np.testing.assert_array_almost_equal(new_pose.position, position)
    np.testing.assert_array_almost_equal(new_pose.orientation, orientation)
