from struct import unpack


class DataSt:

    def __init__(self, form, props, data):
        self.f = form
        self.p = props
        self.d = data
        self.data_dict = {}
        self.data_dict2 = {}
        self.unpack_data = unpack(self.f, self.d)
        self.app_info()
        self.app_info2()

    def app_info(self):
        i = 0
        for prp in self.p:
            self.data_dict[prp] = self.unpack_data[i]
            i += 1

    def app_info2(self):
        self.data_dict2 = {}.fromkeys(self.p, self.unpack_data)

    def pr_info(self):
        print(self.data_dict)
        print(self.data_dict2)
