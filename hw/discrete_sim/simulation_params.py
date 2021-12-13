class SimulationParams:
    
    def __init__(
        self,
        num_standard_beds=28, 
        num_intensive_care_beds=9, 
        mean_standard_treatment=15, 
        mean_intensive_care_treatment=10,
        std_dev_standard_treatment=5,
        standard_care_death_chance=0.0005,
        standard_care_not_sufficient_chance=0.08,
        intensive_care_death_chance=0.0075,
        days_with_new_patients=30,
        mean_new_patients_each_day=3, 
        max_days_without_std_care=10, 
        max_days_without_intensive_care=4
    ):
        self.num_standard_beds = num_standard_beds
        self.num_intensive_care_beds = num_intensive_care_beds
        self.mean_standard_treatment = mean_standard_treatment
        self.mean_intensive_care_treatment = mean_intensive_care_treatment
        self.std_dev_standard_treatment = std_dev_standard_treatment
        self.standard_care_death_chance = standard_care_death_chance
        self.standard_care_not_sufficient_chance = standard_care_not_sufficient_chance
        self.intensive_care_death_chance = intensive_care_death_chance
        self.days_with_new_patients = days_with_new_patients
        self.mean_new_patients_each_day = mean_new_patients_each_day
        self.max_days_without_std_care = max_days_without_std_care
        self.max_days_without_intensive_care = max_days_without_intensive_care

