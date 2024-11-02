class user:
    def __init__(self,data=None):
        if data is None:
            self.id = None
            self.username = None
            self.password = None
            self.capacity = None
        
        else:
            data = data.split(";")
            self.id = int(data[0])
            self.username = data[1]
            self.password = data[2]
            self.capacity = float(data[3])

class user_list:
    def __init__(self) -> None:
        self.list = []
    
    def get_user_by_name(self,name:str):
        i:user
        for i in self.list:
            if i.username == name:
                return i
            

    def get_user_by_id(self,id:int):
        i:user
        for i in self.list:
            if i.id == id:
                return i
            
    def append(self,new_user:user):
        self.list.append(new_user)
        
    