import math

#----global input variables----
AC=8
mode='active' # This must be either 'idle' or 'active', beware of typos! Change with update_mode() to be safe.
DG=math.log(4.5,1.07)/25

#----global dependent variables----
af=2.4+1.5*DG+(0,0.5)[mode=='active']

#----function definitions----
def check_mode():
    if mode not in ('idle','active'):
        print('Error: invalid mode')
    return None

def update_mode(nm):
    global mode
    global af
    if nm not in ('idle','active'):
        print('Error: invalid mode')
        return None
    else:
        mode=nm
        af=2.4+1.5*DG+(0,0.5)[mode=='active']
        return None

def update_DG(ne):
    global DG
    DG=ne
    return None

def AfL(l):
    '''
    Returns the cumulative AS cost of raising an Outsider
    other than Phan to the given level 'l'.
    Expects and returns an integer.
    '''
    if l&1:
        return l*((l+1)//2)
    else:
        return (l//2)*(l+1)

def LfA(a):
    '''
    Returns the highest level of an Outsider other than Phan
    purchasable from level 0 from the given amount of AS 'a',
    as well as the remaining unspent AS, as a 2-tuple of ints.
    '''
    rad=8*a+1
    xp=int(rad**0.5)
    xn=(xp+rad//xp)//2
    while xn-xp!=0:
        xp=xn
        xn=(xp+rad//xp)//2
    l=(xn-1)//2
    if l&1:
        c=l*((l+1)//2)
    else:
        c=(l//2)*(l+1)
    return (l,a-c)

def all(a):
    '''
    Generates a set of tuples of integers representing
    all Outsider allocations possible with the given amount of AS 'a'.
    The tuple is to be interpreted as:
    (Xy,Ch,Po,Bo,Rh,KA,Or,Se,Ph)
    '''
    s={tuple([0,]*8+[a])}
    i=0
    while i<8:
        sn=set()
        for x in s:
            ax=x[-1]
            rad=8*ax+1
            xp=int(rad**0.5)
            xn=(xp+rad//xp)//2
            while xn-xp!=0:
                xp=xn
                xn=(xp+rad//xp)//2
            lmax=(xn-1)//2
            if i==0 and mode!='idle':
                lmax=0
            elif i==1:
                lmax=min(lmax,150)
            for k in range(lmax+1):
                item=list(x)
                item[i]=k
                if k&1:
                    c=k*((k+1)//2)
                else:
                    c=(k//2)*(k+1)
                item[-1]-=c
                sn.add(tuple(item))
        s=sn
        i+=1
    return s

def AfO(O):
    return sum(AfL(l) for l in O[:-1])+O[-1]

def TfA(a):
    '''
    Return the Transcendent Power multiplier as a decimal value
    of type 'float' from a given amount of AS 'a'.
    '''
    return 1.25-0.23*math.exp(-0.0003*a)

def TfO(O):
    '''
    Return the Transcendent Power multiplier as a decimal value
    of type 'float' from a given Outsider allocation as specified
    in the function 'all(a)'.
    '''
    return TfA(AfO(O))

def f_AC():
    if AC<6:
        lcps=math.log(10.0*AC)
    else:
        lcps=(AC-1)*math.log(1.5)+math.log(10.0)
    if mode=='idle':
        return lcps
    elif mode=='active':
        return (2.0+DG)*lcps
    else:
        return "Error: invalid mode"

def f_Po(l):
    return af*math.log(1+10*l**2)

def f_Ch(l):
    return af*l*math.log(20/19)

def f_Ph(l):
    return math.log(1+l)

def f_Xy(l):
    if mode=='idle':
        return l*(2+DG)*math.log(1.5)
    else:
        return 0.0

def f_Se(l,z):
    tc_calc=(1+0.99*l)*(10**(-6)+(10**2-10**(-6))*math.exp(-0.006*math.floor(z/500)))
    tc_cap=max(1.0,min(tc_calc,100.0))
    return DG*math.log(tc_cap)

def f_Rh(l,z):
    pc_calc=20+15*l/4-2*math.floor(z/500)/5
    pc_cap=max(1.0,min(pc_calc,20.0))
    return af*math.log(pc_cap)

def f_Or(l,z):
    t_calc=30+45*l/4-math.floor(z/500)
    t_cap=max(1.0,t_calc)
    return math.log(t_cap)

def f_KA(l,z):
    h_calc=1+2*math.floor(z/500)/25-l/2
    h_cap=max(1.0,h_calc)
    return -math.log(h_cap)

def MpZ(B,z):
    M_calc=10+math.floor(z/500)-100*(1+B/10)
    M_cap=max(2,M_calc)
    return M_cap

def f_Bo(l,z):
    return DG*math.log(MpZ(l,z)/2)

def Hscale(z):
    return min(1.545,1.145+max(0,math.floor(z/500)/1000))

def z_den(z,T):
    return math.log(Hscale(z))-DG*math.log(1.15)-af/5*math.log(T)

def z_num(O,z):
    return f_Xy(O[0])+f_Ch(O[1])+f_Po(O[2])+f_Bo(O[3],z)+f_Rh(O[4],z)+f_KA(O[5],z)+f_Or(O[6],z)+f_Se(O[7],z)+f_Ph(O[8])+f_AC()

def const_est(O,z):
    return z*z_den(z,TfO(O))-z_num(O,z)

def all_init(a,spread):
    s={tuple([0,]*8+[a])}
    T=TfA(a)
    i=0
    while i<3:
        sn=set()
        for x in s:
            ax=x[-1]
            rad=8*ax+1
            xp=int(rad**0.5)
            xn=(xp+rad//xp)//2
            while xn-xp!=0:
                xp=xn
                xn=(xp+rad//xp)//2
            lmax=(xn-1)//2
            if i==0 and mode!='idle':
                lmax=0
            elif i==1:
                lmax=min(lmax,150)
            lrange=set(range(lmax+1))
            if i==1 and mode=='idle':
                exact=(x[0]+1/2)*math.log((20/19)**af,1.5**(2+DG))-1/2
                lrangeb=range(math.floor(exact)-spread,math.ceil(exact)+spread+1)
                if lrangeb[0]>150:
                    lrangeb=(150,)
                lrange&=set(lrangeb)
            elif i==2:
                hscalemin=max(1.145,min(math.ceil(200*1.15**DG*T**(af/5))/200,1.545))
                lT1=5*math.log(hscalemin/1.15**DG,T)
                lT2=5*math.log(1.545/1.15**DG,T)
                exactmin=math.sqrt((x[1]+1/2)*2*lT1/math.log((20/19)**af)+1/16)-1/4
                if mode=='idle':
                    exactmin=math.sqrt((x[0]+1/2)*2*lT1/(2+DG)/math.log(1.5)+1/16)-1/4
                    exactmax=math.sqrt((x[0]+1/2)*2*lT2/(2+DG)/math.log(1.5)+1/16)-1/4
                    lrangeb=range(math.floor(exactmin)-spread,math.ceil(exactmax)+spread+1)
                    lrange&=set(lrangeb)
                elif x[1]==150:
                    lrange=set(entry for entry in lrange if entry>=math.floor(exactmin)-spread)
                else:
                    exactmax=math.sqrt((x[1]+1/2)*2*lT2/math.log((20/19)**af)+1/16)-1/4
                    lrangeb=range(math.floor(exactmin)-spread,math.ceil(exactmax)+spread+1)
                    lrange&=set(lrangeb)
            for k in lrange:
                item=list(x)
                item[i]=k
                if k&1:
                    c=k*((k+1)//2)
                else:
                    c=(k//2)*(k+1)
                item[-1]-=c
                sn.add(tuple(item))
        s=sn
        i+=1
    return s

def zhelp(z,O,c,T):
    return z*z_den(z,T)-z_num(O,z)-c

def z_est(O,c,AS):
    '''
    Supposed to solve the transcension max zone equation for the zone.
    Frequently produces runtime errors from zp and zn alternating instead of converging.
    Needs review.
    '''
    T=TfA(AS)
    z=105
    fz=zhelp(z,O,c,T)
    if fz>0:
        raise ValueError("Error: c too small.")
    elif fz==0:
        return z
    while fz<0:
        z*=2
        fz=zhelp(z,O,c,T)
    if fz==0:
        return z
    zp=z//2
    zn=z
    i=0
    while abs(zn-zp)>0.0000001 and abs(fz)>0.0000001:
        i+=1
        zm=(zp+zn)/2
        fz=zhelp(zm,O,c,T)
        if fz<0:
            zp=zm
        elif fz>0:
            zn=zm
    return zm

def zranges(s,c):
    AS=AfO(next(iter(s)))
    d=dict()
    length=len(s)
    for o in s:
        o_min=tuple(list(o[:-1])+[0])
        o_max=tuple(list(o[:3])+[LfA(o[-1])[0],]*5+[o[-1],])
        d[o]=(z_est(o_min,c,AS),z_est(o_max,c,AS))
    return d

def lrange(i,zr,a):
    lmaxa=LfA(a)[0]
    if i not in range(3,8):
        raise ValueError("Error: invalid outsider index call")
    if i==3:
        lmax=min(lmaxa,math.ceil(10*((8+math.floor(zr[1]/500))/100-1)))
        return tuple(range(lmax+1))
    elif i==4:
        lmax=min(lmaxa,math.ceil(8*math.floor(zr[1]/500)/75))
        lmin=max(1,math.floor(8*math.floor(zr[0]/500)/75-76/15)+1)
        return tuple([0,]+list(range(lmin,lmax+1)))
    elif i==5:
        lmax=min(lmaxa,math.ceil(4*math.floor(zr[1]/500)/25))
        return tuple(range(lmax+1))
    elif i==6:
        lmax=lmaxa
        lmin=max(1,math.floor(4*(math.floor(zr[0]/500)-29)/45)+1)
        return tuple([0,]+list(range(lmin,lmax+1)))
    elif i==7:
        lmax=math.ceil((10**10/(1+(10**8-1)*math.exp(-0.006*math.floor(zr[1]/500)))-100)/99)
        lmax=min(lmaxa,lmax)
        lmin=math.floor((10**8/(1+(10**8-1)*math.exp(-0.006*math.floor(zr[0]/500)))-100)/99)+1
        lmin=max(1,lmin)
        return tuple([0,]+list(range(lmin,lmax+1)))
    else:
        print("Error: didn't catch previous invalid outsider index call error.")
        return None

def all_comp(di):
    '''
    Finishes the allocations initialized by all_init() after they were annotated
    by zranges() with their respective zone ranges, to allow narrowing down the
    ranges of sensible levels for the zone scaling related Outsiders.
    Expects an input dictionary where outsider allocations are keys and zone ranges,
    as given by zranges(), are values.
    Returns a set of completed outsider allocations.
    '''
    d=di.copy()
    i=3
    while i<8:
        dn=dict()
        for x in d:
            for l in lrange(i,d[x],x[-1]):
                item=list(x)
                item[i]=l
                item[-1]-=AfL(l)
                dn[tuple(item)]=d[x]
        d=dn
        i+=1
    return set(d)

def eval_zones(s,c):
    return {o: z_est(o,c,AfO(o)) for o in s}

def pc(R,z):
    return max(0.05,min(1+3*R/16-math.floor(z/500)/50,1.0))

def apc(R,z,T):
    dz=40*math.log(10,T)
    borders=[z-dz,]+list(range(500*math.ceil((z-dz)/500),500*math.floor(z/500)+500,500))+[z,]
    souls=[T**((x-z)/5) for x in borders]
    num=sum(pc(R,borders[i])*(souls[i+1]-souls[i]) for i in range(len(borders)-1))
    den=sum((souls[i+1]-souls[i]) for i in range(len(borders)-1))
    return num/den

def eval_ASgain(d,c,A):
    dn=dict()
    for o in d:
        z=d[o]
        T=TfO(o)
        lpo=math.log(1+10*o[2]**2,10)
        lrh=math.log(apc(o[4],z,T),10)
        dn[o]=(z,5*((z/5-19)*math.log(T,10)+lpo+lrh+math.log(20/(T-1),10))-A)
    return dn

def eval_time(d):
    dn=dict()
    for o in d:
        z=d[o][0]
        B=o[3]
        borders=[0,]+list(range(500*(93+10*B),math.floor(z/500)*500+500,500))+[z,]
        time=sum((MpZ(B,borders[x])-1)*(borders[x+1]-borders[x]) for x in range(len(borders)-1))
        dn[o]=(z,d[o][1],time)
    return dn

def eval_efficiency(d):
    '''
    Output Format:
    (Xy,Ch,Po,Bo,Rh,KA,Or,Se,Ph) : (zone, ASgain, time, efficiency)
    '''
    dn=dict()
    for o in d:
        dn[o]=tuple(list(d[o])+[d[o][1]/d[o][2],])
    return dn

def select_best(d):
    best=max(d, key=lambda k:d[k][3])
    return (best,d[best])

#----main process----
mv=int(input("Do you play active or idle? Type 1 for active or 0 for idle. "))
if mv==1:
    update_mode('active')
elif mv==0:
    update_mode('idle')
else:
    print("Error: invalid input. Restart script.")
if mode=='active':
    AC=int(input("How many Autoclickers do you have assigned to the monster? "))
elif mode=='idle':
    AC=int(input("How many unassigned Autoclickers do you have? "))
print("Please specify the Outsider levels you had during your last transcension.")
print("These are requested in the same order as the ingame Outsiders tab, except Phan coming last.")
O_prev = (int(input("Xyliqil? ")),
    int(input("Chor'gorloth? ")),
    int(input("Ponyboy? ")),
    int(input("Borb? ")),
    int(input("Rhageist? ")),
    int(input("K'Ariqua? ")),
    int(input("Orphalas? ")),
    int(input("Sen-Akhan? ")),
    int(input("Phandoryss? ")))
z_prev = int(input("What was the highest zone you reached during your last transcension? "))
AS_now = int(input("How many Ancient Souls do you have right now? "))
spread_setting = int(input("How far from the estimated optimum would you like to look?\nSmall integer expected.\nLarger numbers cause a more exhaustive search that takes longer\nbut is unlikely to yield better results."))
print("Thank you for your input. Calculations will now commence. Depending on your AS and especially if you play idle, this might take a while.")
c_prev = const_est(O_prev, z_prev)
x = all_init(AS_now,spread_setting)
print(str(len(x))+" initialized combinations.")
x = zranges(x, c_prev)
print("Zone range annotation complete.")
x = all_comp(x)
print(str(len(x))+" completed combinations.")
x = eval_zones(x, c_prev)
print("Zone evaluation complete.")
x = eval_ASgain(x, c_prev, AS_now)
print("Ancient Souls gain evaluation complete.")
x = eval_time(x)
print("Time evaluation complete.")
x = eval_efficiency(x)
print("Efficiency evaluation complete.")
opt = select_best(x)
print("Finished comparing "+str(len(x))+" possible Outsider allocations.")
print("This one is predicted to perform best:")
print("(Xyl, Chor, Pony, Borb, Rhag, K'Ari, Orph, Sen, Phan)")
print(str(opt[0]))
print("predicted highest zone to be reached: "+str(opt[1][0]))
print("predicted ancient souls to be gained: "+str(opt[1][1]))
print("efficiency score: "+str(opt[1][3]))
print("Process completed. Assign Outsider levels and good luck with your next Transcension!")
print("Remember to save your outsider configuration before transcending next time so you can input it again, since this script cannot store it on your hard drive for the next time you run it.")
input("Enter anything to close.")