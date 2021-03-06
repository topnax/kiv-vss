import random
from monitored_resource import MonitoredResource
import simpy
import numpy as np
from sim_stats_plotting import plot_hospital_data
from enum import Enum, auto


class Simulation:
    
    def __init__(self, params):
        self.params = params
    
    def run(self):
        params = self.params
        env = simpy.Environment()
        patient_outcomes = []

        # create a hospital
        hospital = Hospital(
            env, 
            num_standard_beds=params.num_standard_beds, 
            num_intensive_care_beds=params.num_intensive_care_beds, 
            mean_standard_treatment=params.mean_standard_treatment, 
            mean_intensive_care_treatment=params.mean_intensive_care_treatment,
            std_dev_standard_treatment=params.std_dev_standard_treatment,
            standard_care_death_chance=params.standard_care_death_chance,
            standard_care_not_sufficient_chance=params.standard_care_not_sufficient_chance,
            intensive_care_death_chance=params.intensive_care_death_chance
        )

        print(params.days_with_new_patients)
        # run the simulation
        env.process(self.run_hospital(env, hospital, patient_outcomes, 
                    days_with_new_patients=params.days_with_new_patients, 
                    mean_new_patients_each_day=params.mean_new_patients_each_day, 
                    max_days_without_std_care=params.max_days_without_std_care, 
                    max_days_without_intensive_care=params.max_days_without_intensive_care
            )
        )
        print("Hospital events:")
        print("[{day}]", "#{patient_id} (@{day_of_first_hospitalization}) {message}")
        env.run()

        print()
        print("Patient hospitalization outcomes:")
        print("#{patient_id}", "@{day_of_first_hospitalization}: {outcome} at {day}")
        # print patient results
        for (result, patient, day) in patient_outcomes:
            print(f"#{patient.patient_id}", f"@{patient.day_hospitalized}:", result, "at", day)

        print()
        print("Hospital statistics:")
        print("@{day_s}, standard beds: {standard_beds_usage}/{standard_beds_capacity}, intensive care beds: {intensive_care_beds_usage}/{intensive_care_beds_capacity}") 
        # print day statistics
        for (day_s, s), (day_i, i) in zip(hospital.standard_beds.data.items(), hospital.intensive_care_beds.data.items()):
            print(f"@{day_s}, standard beds: {s}/{hospital.standard_beds.capacity}, intensive care beds: {i}/{hospital.intensive_care_beds.capacity}")
        
        self.print_sim_stats(patient_outcomes)

        if params.plot:
            plot_hospital_data(hospital)

    def run_hospital(self, env, hospital, patient_outcomes, days_with_new_patients, mean_new_patients_each_day, max_days_without_std_care, max_days_without_intensive_care):
        patient_id = 0
            
        # simulate days that new patients come for health care
        for i in range(days_with_new_patients):
            for j in range(np.random.poisson(mean_new_patients_each_day)):
                p = Patient(patient_id, max_days_without_intensive_care, max_days_without_std_care, i)
                patient_id += 1
                env.process(p.go_to_standard_care(hospital, env, patient_outcomes))
            # next day  of the simulation
            yield env.timeout(1)
            hospital.monitor()

    def print_sim_stats(self, patient_outcomes):
        # compute the death probability
        deaths_total = 0
        results_dict = {}

        deaths_standard_care = 0
        deaths_intensive_care = 0
        for (result, patient, day) in patient_outcomes:
            results_dict[result] = results_dict.get(result, 0) + 1

        recovered_total = results_dict.get(PatientHospitalizationResult.RECOVERED, 0)
        deaths_std_care_total = results_dict.get(PatientHospitalizationResult.DEATH_STD_CARE, 0)
        deaths_int_care_total = results_dict.get(PatientHospitalizationResult.DEATH_INT_CARE, 0)
        deaths_int_care_std_total = results_dict.get(PatientHospitalizationResult.DEATH_INT_CARE_STD, 0)
        deaths_without_std_care_total = results_dict.get(PatientHospitalizationResult.DEATH_WITHOUT_STD_CARE, 0)
        deaths_without_int_care_total = results_dict.get(PatientHospitalizationResult.DEATH_WITHOUT_INTENSIVE_CARE, 0)
        deaths_total = sum(results_dict.values()) - recovered_total
        patients = sum(results_dict.values())
        print()
        print("Simulation stats:")
        print("patients:", patients)
        print("recovered:", recovered_total)
        print("deaths total:", deaths_total)
        print("deaths standard care total:", deaths_std_care_total)
        print("deaths intensive care total:", deaths_int_care_total)
        print("deaths intensive care requiring standard care:", deaths_int_care_std_total)
        print("deaths requiring standard care and not hospitalized:", deaths_without_std_care_total)
        print("deaths requiring intensive care but kept on standard care:", deaths_without_int_care_total)

        print(f"death probability: {((deaths_total / patients) * 100):.4f}%")
        print(f"probability of not being hospitalized and dying: {((deaths_without_std_care_total / patients) * 100):.4f}%")
        print(f"probability of not being hospitalized at intensive care and dying: {((deaths_without_int_care_total / patients) * 100):.4f}%")


class Hospital:
    def __init__(self, env, num_standard_beds, num_intensive_care_beds, mean_standard_treatment, mean_intensive_care_treatment, std_dev_standard_treatment, standard_care_death_chance, standard_care_not_sufficient_chance, intensive_care_death_chance):
        self.env = env
        # create resources
        self.standard_beds = MonitoredResource(env, num_standard_beds)
        self.intensive_care_beds = MonitoredResource(env, num_intensive_care_beds)

        # define properties of the treatment
        self.mean_standard_treatment = mean_standard_treatment
        self.mean_intensive_care_treatment = mean_intensive_care_treatment
        self.std_dev_standard_treatment = std_dev_standard_treatment
        self.standard_care_death_chance = standard_care_death_chance
        self.standard_care_not_sufficient_chance = standard_care_not_sufficient_chance
        self.intensive_care_death_chance = intensive_care_death_chance

    def monitor(self):
        self.standard_beds.update_data()
        self.intensive_care_beds.update_data()
       

# patient sickness outcomes
class PatientHospitalizationResult(Enum):
    DEATH_STD_CARE = auto()
    RECOVERED = auto()
    DEATH_WITHOUT_STD_CARE = auto()
    DEATH_WITHOUT_INTENSIVE_CARE = auto()
    DEATH_INT_CARE = auto()
    DEATH_INT_CARE_STD = auto()

    def __str__(self):
        return self.name


class Patient:

    def __init__(self, patient_id, limit_of_days_without_intensive_care, limit_of_days_without_standard_care, day_hospitalized):
        self.patient_id = patient_id
        self.limit_of_days_without_intensive_care = limit_of_days_without_intensive_care
        self.days_without_intensive_care = 0
        self.limit_of_days_without_standard_care = limit_of_days_without_standard_care
        self.days_without_standard_care = 0
        self.total_days_at_standard_care = 0
        self.total_days_at_intensive_care = 0
        self.total_days_at_intensive_care_2 = 0
        self.day_hospitalized = day_hospitalized
        self.transfer_to_intensive_care_required = False

    def go_to_standard_care(self, hospital, env, patient_outcomes, days=None):
        # random hospitalization days
        if days is None:
            days = int(max(random.gauss(hospital.mean_standard_treatment, hospital.std_dev_standard_treatment), 0))
        day = 0

        transferred_to_int_care = False
        self.log(env, "requires standard care for", days, "days")

        with hospital.standard_beds.request() as request:
            standard_care_waiting_start = env.now

            # make an attempt to get a standard care bed (wait only for a limited time, die otherwise :/)
            results = yield request | env.timeout(self.limit_of_days_without_standard_care)
            hospital.monitor()

            # the patient was not moved to a standard care bed
            if request not in results:
                self.log(env, "died without standard care")
                patient_outcomes.append((PatientHospitalizationResult.DEATH_WITHOUT_STD_CARE, self, env.now))
                hospital.monitor()
                return

            # print how many days the patient was waiting
            standard_care_waiting_time = env.now - standard_care_waiting_start
            if standard_care_waiting_time > 0:
                self.log(env, f"waited {standard_care_waiting_time} days for standard care")
            self.log(env, f"hospitalized at standard care for {days} days")

            # simulate n days at the standard care bed
            while day < days:
                # one day at standard care
                yield env.timeout(1)
                hospital.monitor()

                # update day count
                day += 1
                self.total_days_at_standard_care += 1
                
                # the patient may have died during the day at a standard care bed
                died = random.random() < hospital.standard_care_death_chance
                
                if died:
                    self.log(env, "died at standard care" ) 
                    patient_outcomes.append((PatientHospitalizationResult.DEATH_STD_CARE, self, env.now))
                    return 
                
                # if the patient did not die he may require to be transfered to a intensive care bed
                if not self.transfer_to_intensive_care_required:
                    self.transfer_to_intensive_care_required = random.random() < hospital.standard_care_not_sufficient_chance
                    self.days_without_intensive_care = 0
                    
                if self.transfer_to_intensive_care_required:
                    # check whether there are any intensive care beds available
                    if hospital.intensive_care_beds.count >= hospital.intensive_care_beds.capacity:
                        # intensive care bed not available
                        self.days_without_intensive_care += 1
                        # check whether the patient requiring intensive care has been too many days on a standard care requiring intensive care
                        if self.days_without_intensive_care > self.limit_of_days_without_intensive_care:
                            self.log(env, "died after waiting for intensive care at standard care for too long")
                            patient_outcomes.append((PatientHospitalizationResult.DEATH_WITHOUT_INTENSIVE_CARE, self, env.now))
                            return 
                    else:
                        # intensive care bed available
                        self.transfer_to_intensive_care_required = False
                        self.log(env, "required int care, transfered after", self.days_without_intensive_care, "days of waiting")
                        day = days
                        transferred_to_int_care = True
                        break
                
        # start a new process if the patient is to be transfered to int. care
        if transferred_to_int_care:
            env.process(self.go_to_intensive_care(hospital, env, patient_outcomes))
            return

        # the patient has recovered
        self.log(env, "recovered at standard care")
        patient_outcomes.append((PatientHospitalizationResult.RECOVERED, self, env.now))

    def go_to_intensive_care(self, hospital, env, patient_outcomes):
        # random hospitalization days
        days = int(max(np.random.exponential(hospital.mean_intensive_care_treatment), 0))
        day = 0

        self.log(env, "hospitalized at intensive care for", days, "days")
            
        with hospital.intensive_care_beds.request() as request:
            # get a bed
            yield request
            while day < days:
                # one day at intensive care
                yield env.timeout(1)
                hospital.monitor()
                day += 1

                # the patient may have died during the day at a intensive care bed
                died = random.random() < hospital.intensive_care_death_chance
                
                if died:
                    self.log(env, "died at intensive care")
                    patient_outcomes.append((PatientHospitalizationResult.DEATH_INT_CARE, self, env.now)) 
                    return

            # patient recovered from intensive care

            # move to a standard bed
            if hospital.standard_beds.count >= hospital.standard_beds.capacity:
                # standard beds are full

                # number of days to recover using the standard care treatment
                days = max(random.gauss(hospital.mean_standard_treatment, hospital.std_dev_standard_treatment), 0)
                
                while day < days:
                    # one day at intensive care (while requiring only standard care)
                    yield env.timeout(1)
                    hospital.monitor()
                    day += 1
                    self.total_days_at_intensive_care_2 += 1

                    # standard beds are not full anymore
                    if hospital.standard_beds.count < hospital.standard_beds.capacity:
                            
                        self.log(env, f"moved to standard care after recovering from intensive care, waited {self.total_days_at_intensive_care_2} days")

                        # start a new process at standard care
                        env.process(self.go_to_standard_care(hospital, env, patient_outcomes, days - day))
                        return
                    else:
                         # the patient may have died during the day at the intensive care bed (requiring only standard care)
                        died = random.random() < hospital.standard_care_death_chance
                        if died:
                            self.log(env, "died in intensive care requiring standard care")
                            patient_outcomes.append((PatientHospitalizationResult.DEATH_INT_CARE_STD, self, env.now))
                            return 
                    self.log(env, "recovered in intensive care requiring standard care")
                    patient_outcomes.append((PatientHospitalizationResult.RECOVERED, self, env.now))
                return
   
            else:
                # recovered from intensive, moved back to standard
                self.log(env, "recovered from intensive, moved to standard")
                hospital.monitor()
                env.process(self.go_to_standard_care(hospital, env, patient_outcomes))
                return
        assert(false)

    def log(self, env, *message):
        print(f"[{env.now}]", f"#{self.patient_id} (@{self.day_hospitalized})", *message)


