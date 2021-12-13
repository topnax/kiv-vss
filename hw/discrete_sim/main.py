import argparse
from os.path import exists 
import sys
import json
from simulation import Simulation

from enum import Enum

class DictObj:
    def __init__(self, in_dict):
        assert isinstance(in_dict, dict)
        for key, val in in_dict.items():
            if isinstance(val, (list, tuple)):
               setattr(self, key, [DictObj(x) if isinstance(x, dict) else x for x in val])
            else:
               setattr(self, key, DictObj(val) if isinstance(val, dict) else val)


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("--num_standard_beds", default=28, help="The number of standard care beds available in the hospital", type=int)
    parser.add_argument("--num_intensive_care_beds", default=9, help="The number of beds at the intensive care available in the hospital", type=int)
    parser.add_argument("--mean_standard_treatment", default=15, help="The mean value of days it takes for a patient at the standard care to recover", type=int)
    parser.add_argument("--mean_intensive_care_treatment", default=10,help="The mean value of days it takes for a patient at the standard care to recover", type=int)
    parser.add_argument("--std_dev_standard_treatment", default=5, help="The deviation value of days it takes for a patient at the standard care to recover", type=int)
    parser.add_argument("--standard_care_death_chance", default=0.0005, help="The chance a patient dies each day at the standard care", type=float)
    parser.add_argument("--standard_care_not_sufficient_chance", default=0.08, help="The chance a patient dies has to be moved to the intensive care", type=float)
    parser.add_argument("--intensive_care_death_chance", default=0.0075, help="The chance a patient dies each day at the intensive care", type=float)
    parser.add_argument("--days_with_new_patients", default=30, help="Number of days new patients are coming to the hospital", type=int)
    parser.add_argument("--mean_new_patients_each_day", default=3, help="Mean value of patients that come each day to the hospital", type=int)
    parser.add_argument("--max_days_without_std_care", default=10, help="The number of days the patient dies if not hospitalized in the standard care", type=int)
    parser.add_argument("--max_days_without_intensive_care", default=4, help="The number of days the patient dies if not hospitalized in the intensive care", type=int)
    parser.add_argument("--config", default=None, help="Path to the configuration file (in JSON format). Individual attributes should follow arguments structure as described in this help message.", type=str)
    

    args = parser.parse_args()

    if args.config is not None:
        print("Config file passed, ignoring any other parameters...")
        assert exists(args.config), "configuration file does not exist"
        file = open(args.config)
        config = json.load(file)
        assert "num_standard_beds" in config, "num_standard_beds not present in the config"
        assert "num_intensive_care_beds" in config, "num_intensive_care_beds not present in the config"
        assert "mean_standard_treatment" in config, "mean_standard_treatment not present in the config"
        assert "mean_intensive_care_treatment" in config, "mean_intensive_care_treatment not present in the config"
        assert "std_dev_standard_treatment" in config, "std_dev_standard_treatment not present in the config"
        assert "standard_care_death_chance" in config, "standard_care_death_chance not present in the config"
        assert "standard_care_not_sufficient_chance" in config, "standard_care_not_sufficient_chance not present in the config"
        assert "intensive_care_death_chance" in config, "intensive_care_death_chance not present in the config"
        assert "days_with_new_patients" in config, "days_with_new_patients not present in the config"
        assert "mean_new_patients_each_day" in config, "mean_new_patients_each_day not present in the config"
        assert "max_days_without_std_care" in config, "max_days_without_std_care not present in the config"
        assert "max_days_without_intensive_care" in config, "max_days_without_intensive_care not present in the config"
        for key, value in config.items():
            if key == "intensive_care_death_chance" or key == "standard_care_death_chance" or key == "standard_care_not_sufficient_chance": 
                assert(type(value) == float)
            else:
                assert(type(value) == int)
        params = DictObj(config)
    else:
        params = args

    simulation = Simulation(params)
    simulation.run()


if __name__ == "__main__":
    main()


