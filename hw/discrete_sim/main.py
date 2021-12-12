import random
import simpy
import numpy as np

from enum import Enum


class MonitoredResource(simpy.Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = {}

    def request(self, *args, **kwargs):
        #self.data[self._env.now] = self.count
        self.update_data()
        return super().request(*args, **kwargs)

    def release(self, *args, **kwargs):
        #self.data[self._env.now] = self.count
        self.update_data()
        return super().release(*args, **kwargs)

    def update_data(self):
        current_count = self.data.get(self._env.now, 0)
        self.data[self._env.now] = max(self.count, current_count)


class Hospital:
    def __init__(self, env, num_standard_beds, num_intensive_care_beds, mean_standard_treatment, mean_intensive_care_treatment, std_dev_standard_treatment, std_dev_intensive_care_treatment, standard_care_death_chance, standard_care_not_sufficient_chance, intensive_care_death_chance):
        self.env = env
        self.standard_beds = MonitoredResource(env, num_standard_beds)
        self.intensive_care_beds = MonitoredResource(env, num_intensive_care_beds)
        self.mean_standard_treatment = mean_standard_treatment
        self.mean_intensive_care_treatment = mean_intensive_care_treatment
        self.std_dev_standard_treatment = std_dev_standard_treatment
        self.std_dev_intensive_care_treatment = std_dev_intensive_care_treatment
        self.standard_care_death_chance = standard_care_death_chance
        self.standard_care_not_sufficient_chance = standard_care_not_sufficient_chance
        self.intensive_care_death_chance = intensive_care_death_chance
        self.standard_care_beds_stats = {}
        self.intensive_care_beds_stats = {}


    def standard_treatment(self):
        yield self.env.timeout(max(random.gauss(self.mean_standard_treatment, self.std_dev_standard_treatment), 0))

    def intensive_care_treatment(self):
        yield self.env.timeout(max(random.gauss(self.mean_intensive_care_treatment, self.std_dev_intensive_care_treatment), 0))

    def monitor(self):
        self.standard_beds.update_data()
        self.intensive_care_beds.update_data()
       

class PatientHospitalizationResult(Enum):
    STANDARD_FULL = 1
    INTENSIVE_FULL = 2
    DEATH_STD_CARE = 3
    MOVED_TO_INTENSIVE = 4
    RECOVERED = 5
    DEATH_WITHOUT_STD_CARE = 6
    DEATH_WITHOUT_INTENSIVE_CARE = 7
    DEATH_INT_CARE = 8
    DEATH_INT_CARE_STD = 9


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

    def go_to_standard_care(self, hospital, env, ret_codes, days=None):
        # random hospitalization days
        if days is None:
            days = max(random.gauss(hospital.mean_standard_treatment, hospital.std_dev_standard_treatment), 0)
        day = 0

        # standard beds are full
        while hospital.standard_beds.count >= hospital.standard_beds.capacity:
            yield env.timeout(1)
            hospital.monitor()
            self.days_without_standard_care += 1
            if self.days_without_standard_care > self.limit_of_days_without_standard_care:
                print("patient", self.patient_id, "died without standard care")
                ret_codes.append((PatientHospitalizationResult.DEATH_WITHOUT_STD_CARE, self, env.now))
                return 
        if self.days_without_standard_care > 0:
            print("paitent", self.patient_id, "waited", self.days_without_standard_care, ", but eventually made it")
            
        transferred_to_int_care = False
        with hospital.standard_beds.request() as request:
            # get a bed
            yield request

            # simulate n days at the standard care bed
            while day < days:
                yield env.timeout(1)
                hospital.monitor()
                # update day count
                day += 1
                self.total_days_at_standard_care += 1
                
                # the patient may have died during the day at a standard care bed
                died = random.random() < hospital.standard_care_death_chance
                
                if died:
                    ret_codes.append((PatientHospitalizationResult.DEATH_STD_CARE, self, env.now))
                    return 

                
                # if the patient did not die he may require to be transfered to a intensive care bed
                transfer_to_intensive_care_required = random.random() < hospital.standard_care_not_sufficient_chance

                if transfer_to_intensive_care_required:
                    # check whether there are any intensive care beds available
                    if hospital.intensive_care_beds.count >= hospital.intensive_care_beds.capacity:
                        self.days_without_intensive_care += 1
                        # check whether the patient requiring intensive care has been too many days on a standard care
                        if self.days_without_intensive_care > self.limit_of_days_without_intensive_care:
                            ret_codes.append((PatientHospitalizationResult.DEATH_WITHOUT_INTENSIVE_CARE, self, env.now))
                            return 
                    else:
                        print(self.patient_id, "required int care, made it after", self.days_without_intensive_care)
                        day = days
                        transferred_to_int_care = True
                        break

        if transferred_to_int_care:
            env.process(self.go_to_intensive_care(hospital, env, ret_codes))
            return


        # the patient has recovered
        ret_codes.append((PatientHospitalizationResult.RECOVERED, self, env.now))

    def go_to_intensive_care(self, hospital, env, ret_codes):

        # random hospitalization days
        days = max(np.random.exponential(hospital.mean_intensive_care_treatment), 0)
        day = 0

        # check whether intensive care beds are full (should not happen)
        if hospital.intensive_care_beds.count >= hospital.intensive_care_beds.capacity:
            print("should not")
            ret_codes.append((PatientHospitalizationResult.INTENSIVE_FULL, self, env.now))
            return
            
        with hospital.intensive_care_beds.request() as request:
            # get a bed
            yield request
            while day < days:
                yield env.timeout(1)
                hospital.monitor()
                day += 1

                # the patient may have died during the day at a intensive care bed
                died = random.random() < hospital.intensive_care_death_chance
                
                if died:
                    ret_codes.append((PatientHospitalizationResult.DEATH_INT_CARE, self, env.now)) 
                    return

            # move to a standard bed
            # standard beds are full
            if hospital.standard_beds.count >= hospital.standard_beds.capacity:

                # number of days to recover using the standard treatment
                days = max(random.gauss(hospital.mean_standard_treatment, hospital.std_dev_standard_treatment), 0)

                while day < days:
                    yield env.timeout(1)
                    hospital.monitor()


                    day += 1
                    self.total_days_at_intensive_care_2 += 1
                    # standard beds are not full
                    if hospital.standard_beds.count < hospital.standard_beds.capacity:
                        env.process(self.go_to_standard_care(hospital, env, ret_codes, days - day))
                        return
                    else:
                         # the patient may have died during the day at a standard care bed
                        died = random.random() < hospital.standard_care_death_chance
                        if died:
                            ret_codes.append((PatientHospitalizationResult.DEATH_INT_CARE_STD, self, env.now))
                            return 
                    ret_codes.append((PatientHospitalizationResult.RECOVERED, self, env.now))
                return
   
            else:
                print("recovered from int, moved to standard")
                env.process(self.go_to_standard_care(hospital, env, ret_codes))
                return
        assert(false)


def run_hospital(env, hospital, ret_codes):
    standard_care_bed_used = []
    intensive_care_bed_used = []
    pi = 0
    for i in range(30):
        for j in range(np.random.poisson(20)):
            p = Patient(pi, 4, 10, i)
            pi += 1
            env.process(p.go_to_standard_care(hospital, env, ret_codes))
        standard_care_bed_used.append(hospital.standard_beds.count) 
        intensive_care_bed_used.append(hospital.intensive_care_beds.count) 
        yield env.timeout(1)
        hospital.monitor()


def main():
    env = simpy.Environment()
    ret_codes = []
    hospital = Hospital(env, 110, 12, 10, 5, 10, 50, 0.0005, 0.08, 0.0075)

    env.process(run_hospital(env, hospital, ret_codes))
    
    env.run()
    for (result, patient_id, day) in ret_codes:
        print("patient:", patient_id.patient_id, f"{patient_id.day_hospitalized}", result, "at", day)

    for (day_s, s), (day_i, i) in zip(hospital.standard_beds.data.items(), hospital.intensive_care_beds.data.items()):
        print("day:", day_s, "standard:", s, "intensive:", i)


if __name__ == "__main__":
    main()


