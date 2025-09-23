"""
Combat calculations developed with the following tools:

- desmos.com:
    - weapons range: https://www.desmos.com/calculator/ekuw0p42lk

"""
from source.classes.ship.ship_class import Ship


class Combat_Calculations:
    def __init__(self):
        pass


    def get_ship_perfect_solution_range(self, ship_object: Ship) -> float:
        """
        Calculates range at which the ship has a perfect firing solution

        :param ship_object: player Ship object
        :param target_range: float indicating how far the target is in Mm
        :return: float indicating perfect firing solution range in Mm
        """

        # sensor firing solution range individual
        solution_range_ir = self.get_sensor_perfect_solution_range(ship_object, 'ir')
        solution_range_lidar = self.get_sensor_perfect_solution_range(ship_object, 'lidar')
        solution_range_radar = self.get_sensor_perfect_solution_range(ship_object, 'radar')

        # 100% firing solution range
        perfect_solution_range = solution_range_ir * solution_range_lidar * solution_range_radar

        return perfect_solution_range


    def get_sensor_perfect_solution_range(self, ship_object: Ship, signature_type: str) -> float:
        """
        Calculates range at which the ship has a perfect firing solution using only one type of sensor

        :param ship_object: player Ship object
        :param signature_type: what sensor is being used to get firing solution range? ('ir', 'lidar', 'radar')
        :param target_range: float indicating how far the target is in Mm
        :return: float indicating perfect firing solution range in Mm
        """
        # setting up vars
        sensor_range: float = ship_object.sensors[f'{signature_type}_sensor']['range_Mm']
        sensor_acc: float = ship_object.sensors[f'{signature_type}_sensor']['accuracy']

        # 100% firing solution range for given sensor
        perfect_solution_range: float = ((sensor_range/ship_object.target_range) ** sensor_acc) * ship_object.target.signature[{signature_type}]

        return perfect_solution_range


    def get_single_mode_firing_solution_percentage(self, ship_object: Ship, signature_type: str) -> float:
        """
        Calculate how strong firing solution is using only one sensor

        :param ship_object: player Ship object
        :param signature_type: what sensor is being used to get firing solution range? ('ir', 'lidar', 'radar')
        :param target_range: float indicating how far the target is in Mm
        :return: float indicating how strong the firing solution is in percentage
        """
        perfect_solution_range = self.get_sensor_perfect_solution_range(ship_object, signature_type, ship_object.target_range)
        solution_percentage = perfect_solution_range/ship_object.target_range

        return solution_percentage


    def get_multi_mode_firing_solution_percentage(self, ship_object: Ship, target_range: float) -> float:
        """
        Calculate how strong firing solution is using a combination of all sensors

        :param ship_object: player Ship object
        :param target_range: float indicating how far the target is in Mm
        :return: float indicating how strong the firing solution is in percentage
        """

        perfect_solution_range = self.get_ship_perfect_solution_range(ship_object, target_range)
        solution_percentage = perfect_solution_range / target_range

        return solution_percentage

