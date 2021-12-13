import matplotlib.pyplot as plt
 

def plot_hospital_data(hospital):
    standard_beds_data = hospital.standard_beds.data
    intensive_care_beds_data = hospital.intensive_care_beds.data
    max_day = max(max(standard_beds_data.values()), max(intensive_care_beds_data.values()))
    
    # x axis values
    x = list(range(0, max_day))

    # corresponding y axis values
    y_standard_beds = [0] * max_day
    for day, beds_used in standard_beds_data.items():
        y_standard_beds[day] = beds_used

    y_intensive_beds = [0] * max_day
    for day, beds_used in intensive_care_beds_data.items():
        y_intensive_beds[day] = beds_used
     
    # plotting the points
    plt.plot(x, y_standard_beds, label="Standard care beds used")
    plt.plot(x, y_intensive_beds, label="Intensive care beds used")
    plt.plot(x, [hospital.standard_beds.capacity] * max_day, label="Standard care capacity", linestyle="dashed")
    plt.plot(x, [hospital.intensive_care_beds.capacity] * max_day, label="Intensive care capacity", linestyle="dashed")
     
    # naming the x axis
    plt.xlabel('Simulation day')
    # naming the y axis
    plt.ylabel('Beds used')

    # show a legend
    plt.legend() 

    # giving a title to the graph
    plt.title('Hospital bed usage')
     
    # function to show the plot
    plt.show()


