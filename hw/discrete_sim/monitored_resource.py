import simpy

# a class that extends the simpy.Resource in order to provide monitoring capabilities
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

