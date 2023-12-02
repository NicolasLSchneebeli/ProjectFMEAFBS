import pandas as pd
import datetime as dt
import numpy as np
import random as rd
import time
import os 
import glob
#Funciton to run the simulation 
def State_machine(components, behaviour,link_matrix,attrs): 
    tick=0
    matrix=np.copy(link_matrix)
    """MAKE A WAY TO RESTART THE LINK MATRIX EACH INTERACTION!!!!"""
    for beh in behaviour:
        beh.state= True
    for component in components:
                for propriety in component.attribute: 
                    propriety.state=True
                    
    status,erro= check(component=components)
    df= pd.DataFrame(columns= ['Tick','Attribute','Component','Origin'])
    
    if status == True:
        stt=time.time()
        while all(behavior.state==True for behavior in behaviour):
            print(f'============================CURRENTLY ON TICK {tick}===============================')
            print(f'----------------------------Proprieties-------------------------------')
            for component in components:
                for propriety in component.attribute: 
                    #IF ATTRIBUTE HAS NOT FAILED YET CONTINUE WITHIN THE LOOP
                    if propriety.state == True:
                        risk= propriety.risk
                        states = ["Working", "Failed"]
                        weights = [100-risk,risk]
                        result= rd.choices(states,weights,k=1)[0]
                                    
                        if result == "Failed":
                            propriety.state=False
                            print(f"{propriety.name} from {propriety.component.name} *just* failed on tick: {tick}")
                            failures=list(propriety.FailureMode.keys())
                            chances=[propriety.FailureMode[i] for i in failures]
                            # if chances == []:
                            propriety.addFailedTick(tick=tick,data=df,origin=propriety)
                            # else:
                            #     result=rd.choices(failures,chances,k=1)[0]
                            #     propriety.addFailedTick(tick=tick,data=df,origin=f'self ({result})')

                            
                        else:
                            print(f"{propriety.name} from {propriety.component.name} is {result}")

                            
                        """When the state of the attribute is false,
                        meaning that it has failed."""      
                    else:
                        '''Check if it is time yet for him to failed! (Right now just time, cause of implementation, 
                            perhaps it is a good alternative since is easy to determine unlike temperature for exemple, 
                            which I imagine taking a lot of the memory of the PC. )'''
                        print(f"{propriety.name} from {propriety.component.name} failed on tick {propriety.FailedTick}, which is {tick-propriety.FailedTick} ticks ago")
                        
                        """Getting the links of the each attribute."""
                        i = attrs.index(propriety)
                        for j in range(matrix.shape[1]):
                            '''Relating the columns and getting the links active for this attribute
                            REVISE THIS CONDITION UNDER HERE!!'''
                            if sum(matrix[i,j]) > 0:
                                if tick -propriety.FailedTick >= matrix[i, j, 1]:
                                    risk= matrix[i, j, 0]
                                    states_ = ["Working", "Failed"]
                                    weights = [100-risk,risk]
                                    resultinf= rd.choices(states_,weights,k=1)[0]
                                    if resultinf == "Failed":
                                        attrs[j].getInfected(t=tick,df=df,origin=propriety)
                                        matrix[i,j]=[0,0]
                                        matrix[j,i]=[0,0]
                                        print(f"{attrs[j].name} from {attrs[j].component.name} was infected by {propriety.name}")
                                else:
                                    pass
                            else:
                                pass
                             
            print(f'----------------------------Behaviour-------------------------------')
            for beh in behaviour:
                beh.checkCondition()
            tick +=1
            time.sleep(3)
        else:
            toSave(df=df,behaviour=behaviour,start_time=stt)

    else:
        print(erro)
#NOTE: Remove the error for append method is a good way to improve the quality of the display and the results
        
        
        
#Checking for name erros, attributes without links and component list empty! 
def check(component):
    component_name= set()
    if component== []:
        erro=('Component list is empty!')
        return False, erro
    for comp in component:
        if comp.name.lower() in component_name:
            erro= ('Two or more components with the same name! \n Try adding numbers. F.e. Component1 and Component2 instead of Component and Component')
            return False,erro
        component_name.add(comp.name.lower())
        if comp.attribute == []:
                erro=('There is a component(s) without attribute. Please add an attribute')
                return False,erro
    else:
        erro= None
        return True,erro
    
    
def toSave(df,behaviour,start_time):
    errormsg=[]
    Beh_Failure = [beh for beh in behaviour if not beh.state]
    for beh in Beh_Failure:
        mensagem_erro = f'`{beh.name} failed cause conditions where achivied: {[i.name for i in beh.condition]} FAILED'
        df = df.append({'Failed Behaviour': mensagem_erro}, ignore_index=True)
    # df = df.append(pd.Series(f'Behaviour failed becaused: {[i.name for i in beh.condition for beh in Beh_Failure]}', index=df.columns), ignore_index=True)
    df.to_csv(f'Simulation/Simulation_{dt.datetime.now().day}_{dt.datetime.now().month}_{dt.datetime.now().year}_{dt.datetime.now().hour}_{dt.datetime.now().minute}.csv',index=False)
    time.sleep(1)
    print('===================================DONE================================================')
    print(f'CSV saved in: Simulation/Simulation_{dt.datetime.now().day}_{dt.datetime.now().month}_{dt.datetime.now().year}_{dt.datetime.now().hour}_{dt.datetime.now().minute}.csv')
    print(f'Time to complete {time.time()- start_time} seconds')
    """cant save in a excel file. Dont know why yet, but its not priority i think.""" 



''''RIGHT NOW I HAVE TO DO IT MANUALLY'''
def createMatrix(components):
    attrs=[]
    for component in components:
        for propriety in component.attribute:
            attrs.append(propriety) 
            
    return np.zeros((len(attrs),len(attrs),2),dtype=int),attrs

def createLink(matrix,attribute_list,attribute1,attribute2,risk,time):
    """Finding the index related to the attributes"""   
    i = attribute_list.index(attribute1)
    j = attribute_list.index(attribute2)
    
    '''Adding/Updating the matrix for the values for the link with RISK, TIME'''
    matrix[i, j] = [risk,time] 
    matrix[j, i] = [risk,time]
    
    
    



'''
YET TO BE IMPLEMENTED PROPERLY
'''  
def analysis(path):
    path=os.path.join(path)
    csv_files = glob.glob(os.path.join(path, "*.csv")) 
    dfs=[]
    for f in csv_files:
        df_ = pd.read_csv(f)
        dfs.append(df_)
    df = pd.concat(dfs, ignore_index=True)
    
    return df