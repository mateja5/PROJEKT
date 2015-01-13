import sqlite3
from datetime import*

datoteka_baze = "Baza.sqlite3"


# odpri projekt
def dodaj_projekt(sifra_projekta, avtor, kam, year,month,day,sez_delov=[]): #DELA :)  #sez_delov kot seznam parov recimo [('vfrvfr', 5),('vrgv463',10),('4343212', 20)]
    predvidoma=date(year, month, day)
    danes=date.today()
    #if (predvidoma-danes).days < 0: raise Exception('Ne moreš zaključiti projekta pred današnjim dnem')
    c = baza.cursor()
    c.execute("""INSERT INTO Projekti
                             (šifra_projekta,id_avtorja,za_kam, predvidoma_koncano) VALUES
                             (?,?,?,?)""",[sifra_projekta, avtor, kam, predvidoma])   #avtorje bo izbiral prek seznama
    zapStProj=c.lastrowid
    c.close()
    if sez_delov:
        dodaj_dele(zapStProj, sez_delov)
    return
def dodaj_dele(zapStProj, sez_delov): #DELA :)  #sez_delov kot seznam parov recimo [('sifra', 5),('vrgv463',10),('4343212', 20)]
    c=baza.cursor()
    for d in sez_delov:
        c.execute("""SELECT id_dela FROM Sestavni_deli WHERE sifra=?""",[d[0]])
        zapStDela=c.fetchone()[0]
        c.execute("""INSERT INTO Deli_za_projekt
                             (id_projekta,id_dela,kolicina_pri_projektu) VALUES
                             (?,?,?)""",[zapStProj,zapStDela,d[1]])
    c.close()
    return

def dodaj_zaposlenega(i,p):  # DELA :)
    c=baza.cursor()
    c.execute("""INSERT INTO Avtorji (ime, priimek) VALUES (?,?)""",[i,p])
    c.close()
    return

#ali je projekt že zakljucen, DELA :)
def ali_je_zakljucen(sifra):
    c = baza.cursor()
    c.execute("""SELECT koncano FROM Projekti WHERE šifra_projekta=?""",[sifra])
    konec=c.fetchone()  #vrne vrednost ali pa vrne None ce ni podatka
    if konec is None:
        raise Exception('Projekt ne obstaja!')   #projekt ne obstaja 
    elif konec[0] is None:
        return False
    else:
        return True  #prvi element ker fetchone vrne n-terico oz 1terico

# ali je zakljucen projekt zamujal, DELA :)
def je_zamujal_projekt(sifra_projekta):
    if ali_je_zakljucen(sifra_projekta)==False:
        return 'Projekt še ni zakljucen!'
    else:
        c = baza.cursor()
        c.execute("""SELECT predvidoma_koncano,koncano FROM Projekti WHERE šifra_projekta=?""",[sifra_projekta])
        (d1,d2)=c.fetchone()
        if (d1-d2).days == 0: return 'Zakljucen tocno na predvideni dan.'
        elif (d1-d2).days > 0: return 'Projekt je bil zakljucen '+str((d1-d2).days)+' dni prej.'   
        elif (d1-d2).days < 0: return 'Projekt je bil zamujal '+str((d2-d1).days)+' dni.' 


# zakljuci projekt - plus poraba delov DELA :)  
def zakljuci_projekt(sifra,y=None,m=None,d=None):  
    if ali_je_zakljucen(sifra): return 'Projekt je že zakljucen.'
    if y==None and m==None and d==None:
        datum=date.today()
    else: datum=date(y,m,d)
    porabaDelovPriProjektu(sifra)
    c = baza.cursor()
    c.execute("""UPDATE Projekti SET koncano=? WHERE šifra_projekta=?""",[datum, sifra])
    c.close()
    return  
def porabaDelovPriProjektu(sifra): ## DELA :) # sezDelovProjekta kot [(id_dela, kolicina_pri projektu, kolicina_porabljenih_delov)]
    c=baza.cursor()
    c.execute("""SELECT id_projekta FROM Projekti WHERE šifra_projekta=?""",[sifra])
    id_proj=c.fetchone()[0]
    c.execute("""SELECT id_dela,kolicina_pri_projektu,koliko_porabljenih_delov FROM Deli_za_projekt WHERE id_projekta=?""",[id_proj])
    sezDelovProjekta=c.fetchall()
    for d in sezDelovProjekta:
        c.execute("""SELECT kolicina_na_zalogi FROM Sestavni_deli WHERE id_dela=?""",[d[0]])
        prej=c.fetchone()[0]
        ze_porabljenih=(0 if d[2]==None else d[2])
        if prej < (d[1]-ze_porabljenih): raise Exception('Ni dovolj količin sestavnih delov na zalogi!')
        nova_kolicina=prej-(d[1]-ze_porabljenih)
        c.execute("""UPDATE Sestavni_deli SET kolicina_na_zalogi=? WHERE id_dela=?""",[nova_kolicina, d[0]])
        c.execute("""UPDATE Deli_za_projekt SET koliko_porabljenih_delov=? WHERE (id_projekta=? AND id_dela=?)""",[d[1],id_proj,d[0]])
    c.close()
    return


# poraba delov nedokončanega projekta
def poraba_delov_nedokončanega_projekta(sifra_proj, sezDelov):  #sezDelov [(sifraDela, koliko)]
    c=baza.cursor()
    c.execute("""SELECT id_projekta FROM Projekti WHERE šifra_projekta=?""",[sifra_proj])
    zapStProj=c.fetchone()[0]
    for d in sezDelov:
        c.execute("""SELECT id_dela FROM Sestavni_deli WHERE sifra=?""",[d[0]])
        IDdela=c.fetchone()[0]
        c.execute("""SELECT kolicina_na_zalogi FROM Sestavni_deli WHERE id_dela=?""",[IDdela])
        prej=c.fetchone()[0]
        if prej < d[1]: raise Exception('Ne moreš porabiti več kot pa imaš!')
        c.execute("""UPDATE Deli_za_projekt SET koliko_porabljenih_delov=? WHERE (id_projekta=? AND id_dela=?)""",[d[1],zapStProj,IDdela])
        nova_kolicina=prej-d[1]
        c.execute("""UPDATE Sestavni_deli SET kolicina_na_zalogi=? WHERE (id_projekta=? AND id_dela=?)""",[nova_kolicina,zapStProj,IDdela])
    return

    

# ali je dovolj delov za nek projekt - katerih in koliko ni
def kaj_manjka_za_projekt(sifra_projekta):  # DELA :)
    if ali_je_zakljucen(sifra_projekta): return 'Projekt je že zakljucen.'
    c = baza.cursor()
    c.execute("""SELECT id_projekta FROM Projekti WHERE šifra_projekta=?""",[sifra_projekta])
    zapStProj=c.fetchone()[0]
    c.execute("""SELECT Deli_za_projekt.id_dela,Deli_za_projekt.kolicina_pri_projektu, Deli_za_projekt.koliko_porabljenih_delov,Sestavni_deli.kolicina_na_zalogi
              FROM Deli_za_projekt JOIN Sestavni_deli ON Sestavni_deli.id_dela=Deli_za_projekt.id_dela WHERE Deli_za_projekt.id_projekta=?""",[zapStProj])
    sezDelovKolicina=c.fetchall()
    manjka=[]
    for d in sezDelovKolicina:
        if (d[1]-d[2])>d[3]: manjka+=[(d[0],d[1]-d[2]-d[3])]   
    c.close()
    if manjka!=[]: return manjka
    return 'NIČ'

# koliko vseh delov manjka za vse projekte - za naročilo # DELA :)
def kaj_narocit(): 
    c = baza.cursor()
    c.execute("""SELECT šifra_projekta FROM Projekti""")
    sezProj=c.fetchall()
    sezNarocil=[]
    for proj in sezProj:
        sifra=proj[0]
        posamezen=kaj_manjka_za_projekt(sifra)
        if isinstance(posamezen,list):
            sezNarocil+=posamezen
    c.close()
    if sezNarocil!=[]: return sezNarocil
    return 

# dobili novo pošilko delov 
def nova_posiljka_delov(sez_delov=[]):  # DELA :) #sez_delov kot seznam parov recimo [(1526,'vfrvfr', 5),(45861,'vrgv463',10),(4563,'4343212', 20)]
    if sez_delov==[]:
        sez_delov=kaj_narocit()
        if not isinstance(sez_delov,list):return #če ni potrebno nič naročiti in nismo dobili nove pošiljke
    c = baza.cursor()
    for d in sez_delov:
        c.execute("""INSERT INTO Sestavni_deli(sifra,opis,kolicina_na_zalogi) VALUES
                  (?,?,?)""",[d[0],d[1],d[2]])
    c.close()
    return
        

#prikljucimo se na bazo
baza = sqlite3.connect(datoteka_baze, isolation_level=None, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)

