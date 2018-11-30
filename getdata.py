import sys,os,random,csv
import time,datetime
import help
import configparser

class cfinfo:
    def __init__(self,configfile):
        self.configfile = configfile
        self.villagecode=''
        self.HoleNum=0 #总井数量
        self.TotalArea=0 #总面积
        self.AreaPerOne=0 #人均面积
        self.PeoplesPerFamily_max=0 #户最大人数
        self.PeoplesPerFamily_min=0 #户最小人数
        self.WaterPerM_max=0 #亩均水量最大
        self.WaterPerM_min=0 #亩均水量最小
        self.FirstScale_max=0 #单井比例最大（0-1）
        self.FirstScale_min=0 #单井比例最小（0-1）
        self.WEScale_max=0 #水电系数最大
        self.WEScale_min=0 #水电系数最小
        self.HoleWaterPerHour_min=0 #井出水量最小
        self.HoleWaterPerHour_max=40 #井出水量最大

    def loadConfig(self):
        try:
            cf = configparser.ConfigParser()
            cf.read(self.configfile)
            self.villagecode = cf.get('base','villagecode')
            self.HoleNum = cf.getint('base','HoleNum')
            self.TotalArea=cf.getfloat('base','TotalArea') 
            self.AreaPerOne=cf.getfloat('base','AreaPerOne') 
            self.PeoplesPerFamily_max=cf.getint('base','PeoplesPerFamily_max') 
            self.PeoplesPerFamily_min=cf.getint('base','PeoplesPerFamily_min') 
            self.WaterPerM_max=cf.getfloat('base','WaterPerM_max') 
            self.WaterPerM_min=cf.getfloat('base','WaterPerM_min') 
            self.FirstScale_max=cf.getfloat('base','FirstScale_max') 
            self.FirstScale_min=cf.getfloat('base','FirstScale_min') 
            self.WEScale_max=cf.getfloat('base','WEScale_max') 
            self.WEScale_min=cf.getfloat('base','WEScale_min') 
            self.HoleWaterPerHour_min=cf.getfloat('base','HoleWaterPerHour_min')
            self.HoleWaterPerHour_max=cf.getfloat('base','HoleWaterPerHour_max')
        except Exception as e:
            print('异常类型：',e.__class__,';异常原因：',e)

class MyDataMaker:
    def __init__(self,mycfinfo,sPath):
        self.xconfig = mycfinfo
        self.sPath = sPath
        self.xUsers=[[]]
        self.xHoles=[[]]
        self.xAreas=[[]]
        pass

    def LoadBaseInfo(self):
        csv_file = csv.reader(open(self.sPath + '\\users.csv','r'))
        self.xUsers=[]
        for row in csv_file:
            self.xUsers.append(row)
        
        csv_file = csv.reader(open(self.sPath + '\\holes.csv','r'))
        self.xHoles=[]
        for row in csv_file:
            self.xHoles.append(row)

        csv_file = csv.reader(open(self.sPath + '\\areas.csv','r'))
        self.xAreas=[]
        for row in csv_file:
            self.xAreas.append(row)




    def MakeBaseDataAndSave(self):
        self.MakeUserInfos()
        self.MakeHoleInfos()
        self.MakeUserAreaInfos()

    def MakeUserInfos(self):
        totalUserNum = int(self.xconfig.TotalArea / self.xconfig.AreaPerOne)
        fm=[]

        while totalUserNum > self.xconfig.PeoplesPerFamily_max:
            m1=random.randint(self.xconfig.PeoplesPerFamily_min,self.xconfig.PeoplesPerFamily_max)
            fm.append(m1)
            totalUserNum=totalUserNum-m1

        fm.append(totalUserNum)

        mUsers = [[] for i in range(len(fm))]
        xhelp = help.Help()
        for i in range(len(fm)):
            mUsers[i].append('{}{:04d}'.format(self.xconfig.villagecode,i+1))
            mUsers[i].append(xhelp.GetRandomName())
            mUsers[i].append('{}'.format(fm[i]*self.xconfig.AreaPerOne))
        self.xUsers = mUsers
        out = open(self.sPath + '\\users.csv','a', newline='')
        csv_write = csv.writer(out,dialect='excel')
        csv_write.writerows(mUsers)

        
    def MakeHoleInfos(self):
        mHoles = [[] for i in range(self.xconfig.HoleNum)]
        for i in range(self.xconfig.HoleNum):
            mHoles[i].append('{}{:04d}'.format(self.xconfig.villagecode,i+1))
            mHoles[i].append('#{}'.format(i+1))
            mHoles[i].append(random.uniform(self.xconfig.WEScale_min,self.xconfig.WEScale_max))
            mHoles[i].append(random.uniform(self.xconfig.HoleWaterPerHour_min,self.xconfig.HoleWaterPerHour_max))
        self.xHoles = mHoles
        out = open(self.sPath + '\\holes.csv','a', newline='')
        csv_write = csv.writer(out,dialect='excel')
        csv_write.writerows(mHoles)

    def MakeUserAreaInfos(self):
        mAreas=[[] for i in range(len(self.xUsers)*2)]
        i=0
        for i in range(len(self.xUsers)):
            mAreas[i*2].append(self.xUsers[i][0])
            mAreas[i*2].append(self.xHoles[random.randint(0,len(self.xHoles)-1)][0])
            mAreas[i*2].append(float(self.xUsers[i][2])*random.uniform(self.xconfig.FirstScale_min,self.xconfig.FirstScale_max))
            mAreas[i*2+1].append(self.xUsers[i][0])
            mAreas[i*2+1].append(self.xHoles[random.randint(1,len(self.xHoles)-1)][0])
            mAreas[i*2+1].append(float(self.xUsers[i][2])-float(mAreas[i*2][2]))

        self.xAreas = mAreas
        out = open(self.sPath + '\\areas.csv','a', newline='')
        csv_write = csv.writer(out,dialect='excel')
        csv_write.writerows(mAreas)


    def MakeWaterInfos(self,StartDatetime,TimeScaleList,sfname):
        #分10天灌溉完成，时间，天数
        xsum=0
        for i in TimeScaleList:
            xsum=xsum+i
        vUseWater=[[] for i in range(len(TimeScaleList))]

        AreaPos=0
        for i in range(len(TimeScaleList)):
            vmax = int(len(self.xAreas)*TimeScaleList[i]/xsum)
            for j in range(vmax):
                vUseWater[i].append(self.xAreas[AreaPos])
                AreaPos=AreaPos+1
        while AreaPos < len(self.xAreas) :
            vUseWater[i].append(self.xAreas[AreaPos])
            AreaPos=AreaPos+1

        holetimes=[]

        dstart = datetime.datetime.strptime(StartDatetime,'%Y-%m-%d %H:%M:%S')
        dtimespan = datetime.timedelta(days=1)
        wis=[[] for i in range(len(self.xAreas))]

        wispos=0
        for vw in vUseWater:
            #重新装载时间
            for i in range(len(self.xHoles)):
                holetimes.append(dstart.strftime('%Y-%m-%d %H:%M:%S'))
            dstart=dstart+dtimespan
            for ia in vw:
                wis[wispos].append(ia[0])
                wis[wispos].append(ia[1])
                wis[wispos].append(ia[2])
                fw = float(ia[2])*random.uniform(self.xconfig.WaterPerM_min,self.xconfig.WaterPerM_max)
                Holepos = int(ia[1][-4:])-1
                fe = fw/float(self.xHoles[Holepos][2])
                ft = float(fw/float(self.xHoles[Holepos][3])) #hour
                timespan = datetime.timedelta(hours=ft)
                ftstart = holetimes[Holepos]
                start = datetime.datetime.strptime(ftstart,'%Y-%m-%d %H:%M:%S')
                end = start + timespan
                holetimes[Holepos] =end.strftime('%Y-%m-%d %H:%M:%S')

                wis[wispos].append(fw)
                wis[wispos].append(fe)
                wis[wispos].append(ftstart)
                wis[wispos].append(ft*60)
                wispos = wispos+1
                
        out = open(self.sPath + '\\' + sfname,'a', newline='')
        csv_write = csv.writer(out,dialect='excel')
        csv_write.writerows(wis)




def main():

  
    mhelp = help.Help()
    curpath = mhelp.GetCurPath()

    cfi = cfinfo(curpath+'\\config.ini')
    cfi.loadConfig()
    
    myarg = sys.argv[1]
    dm = MyDataMaker(cfi,curpath)
    if(myarg=='mb'):
        dm.MakeBaseDataAndSave()
    elif (myarg=='mu'):
        dm.LoadBaseInfo()
        argstr = sys.argv[4][1:-1]
        argstrarr=argstr.split(',')
        argarr=[]
        for i in argstrarr:
            argarr.append(int(i))

        sstime = sys.argv[2]+' '+sys.argv[3]
        dm.MakeWaterInfos(sstime,argarr,sys.argv[5])
    elif (myarg=='help'):  
        print("产生基础数据："+"python getdata.py mb")
        print("产生用水数据："+"python getdata.py mu 2018-3-28 08:01:01 [1,3,8,9,11,12,7,5,4,3,1] useWater1.csv")
        


if __name__ == '__main__':
    main()



        