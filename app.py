import SQLServer, MailGonder, CihazBilgi, Sifreleme
import IndexYorum, Formatlama, AdminModelAcma
import time, random
from ButunModeller import ModelSorgula
from flask import Flask, render_template, url_for, redirect, request, session
from datetime import datetime
from importlib import reload
#######################################################################################################################################################
#######################################################################################################################################################
#######################################################################################################################################################
app = Flask(__name__)
SessionID = str(random.randint(100000, 200000))
app.secret_key = SessionID
AdminUlasim    = False
UserUlasim     = False
SayfaUserID    = 0
SiteSahibi = SQLServer.DegerGetir("select Sutun01 FROM SKWebSabitler")
Unvan      = SQLServer.DegerGetir("select Sutun02 FROM SKWebSabitler")
ClientAdi  = ""
#######################################################################################################################################################
#######################################################################################################################################################
#######################################################################################################################################################
@app.route('/')
def index():
     global SiteSahibi, Unvan 
     reload(IndexYorum)
     SiteSahibi = SQLServer.DegerGetir("SELECT Sutun01 FROM SKWebSabitler")
     Unvan = SQLServer.DegerGetir("SELECT      Sutun02 FROM SKWebSabitler")
     return render_template('index.html', SiteSahibi=SiteSahibi, Unvan=Unvan, ClientAdi=ClientAdi, ToplamModel=IndexYorum.ToplamModel, RastGeleSecim=IndexYorum.Rastgele, SonProje=IndexYorum.SonProje, AbonelikPaket=IndexYorum.APaket, WSabit=IndexYorum.WSabit)
#######################################################################################################################################################
#######################################################################################################################################################
#######################################################################################################################################################
@app.route('/MesajGonder', methods=["POST"])
def AnaSayfadanMesajGonder():
     UserName = request.form.get("AdSoyad")
     UserMail = request.form.get("MailAdres")
     UserPhone = request.form.get("Telefon")
     Konu = request.form.get("Konu")
     Mesaj = request.form.get("Mesaj")
     MesajGovdesi =  f"{"-"*50}\n"
     MesajGovdesi += f"Mesajı Gönderenin Konusu: {Konu}\n"
     MesajGovdesi += f"Mesajı Gönderenin Adı Soyadı: {UserName}\n"
     MesajGovdesi += f"Mesajı Gönderenin Mail Adresi: {UserMail}\n"
     MesajGovdesi += f"Mesajı Gönderenin Telefonu: {UserPhone}\n"
     MesajGovdesi += f"Mesaj Tarih/Saati: {datetime.now()}\n"
     MesajGovdesi += f"{"-"*50}\n"
     MesajGovdesi += f"Mesaj Gövdesi:\n{Mesaj}.\n"
     MesajGovdesi += f"{"-"*50}\n"
     MailGonder.MailGonderme(IndexYorum.WSabit[0]["Sutun08"], f"Ana Sayfadan {UserName} Mesaj Gönderdi...", MesajGovdesi)
     return render_template("MsgMesajAlindi.html")
#######################################################################################################################################################
#######################################################################################################################################################
#######################################################################################################################################################
@app.route("/UyelikTalepEdildi.html", methods=["POST"])
def UyelikTalep():
     Kontrol = False
     Mukerrer = False
     Durum = request.form.get("check") 
     
     if Durum is None:
          Mesaj1="Kullanım şarlarımızı Kabul Etmelisiniz"
          Mesaj2="Aksi Halde Üyelik Talebiniz Kabul Edilmeyecektir"
          return render_template("MsgStop.html", Mesaj1=Mesaj1, Mesaj2=Mesaj2)
     else:
          try:
               Sifre1 = request.form.get("Sifre1")
               Sifre2 = request.form.get("Sifre2")
               if Sifre1 == Sifre2:
                    Ad = request.form.get("Ad").upper().strip()
                    Soyad = request.form.get("Soyad").upper().strip()
                    GSMNo = request.form.get("GsmNo").upper().strip()
                    MailAdres = request.form.get("MailAdres").lower().strip()
                    UserName=request.form.get("UserName").lower().strip()
                    MailAdres=MailAdres.lower().strip()
                    Paket=request.form.get("Abonelik").upper().strip()
                    Users = SQLServer.Sorgula(f"SELECT * FROM SKUsers WHERE RTRIM(UserMailAdress)='{MailAdres}'")
                    ##Burada Blokaj kontrolleri yapılacak....
                    if len(Users) > 0:
                         if Users[0]["IsBlock"]:
                              #Bu Mail Adresi Blokeli
                              Kontrol=False
                              Mesaj1="BLOKELISINIZ"
                              Mesaj2="TEKRAR ABONE OLAMAZSINIZ"
                              return render_template("MsgStop.html", Mesaj1=Mesaj1, Mesaj2=Mesaj2)
                         else:
                              #Bu Mail Adresi Kullanılıyor
                              Users = SQLServer.Sorgula(f"SELECT * FROM SKUsers WHERE RTRIM(UserMailAdress)='{MailAdres}' AND RTRIM(UserName)='{UserName}'")
                              if len(Users) > 0:
                                   Kontrol=False
                                   Mesaj1="Mail Adresi & Kullanıcı Adı Hatası"
                                   Mesaj2="Başka Bir Üye Tarafından Kullanılıyor..."
                                   return render_template("MsgStop.html", Mesaj1=Mesaj1, Mesaj2=Mesaj2)
                              else:
                                   Kontrol=True
                                   Mukerrer=True
                    else:
                         Kontrol=True 
                         Mukerrer=False
               else:
                    Kontrol=False
                    Mesaj="Sifreler Birbiriyle Aynı Olmalıdır..."
                    return render_template("UyeOlun.html", Mesaj=Mesaj)
          except Exception as e:
               Kontrol=False
               Mesaj="Hata Meydana Geldi. Tekrar Deneyiniz..."
               return render_template("UyeOlun.html", Mesaj=Mesaj)

          if Kontrol:
               #Kayıt İşlemlerine geldim
               RS = random.randint(100000, 999999)
               BirlesikAd = Ad + ' ' + Soyad
               HashPass = str(Sifreleme.VeriyiSifrele(Sifre1))
               SQL = "INSERT INTO SKUsers (IsAdmin, UserAuth, VerifyMailCode, UserAdiSoyadi, UserName, PassWord, UserGSMNumber, UserMailAdress, IsBlock, PaketAdi, OnOff) "
               SQL += f" VALUES (0, '', {RS}, '{BirlesikAd}', '{UserName}', '{HashPass}', '{GSMNo}', '{MailAdres}', 0, '{Paket}', 0)"
               Durum = SQLServer.Calistir(SQL)
               if Durum:
                    Mesaj1 = "Teşekkür Ederiz"
                    Mesaj2 = "Talebinizi Aldık Sizden Abonelik Bedeli Dekontunu Bekliyoruz"
                    if Mukerrer:
                         Mesaj2 += " (Mukerrer Talep)"
                    return render_template("MsgMesajAlindi.html", Mesaj1=Mesaj1, Mesaj2=Mesaj2)
               else:
                    Mesaj1="Ooops!!!"
                    Mesaj2="Beklenilmeyen Bir Hata Meydana Geldi (SQL)"
                    return render_template("MsgError.html", Mesaj1=Mesaj1, Mesaj2=Mesaj2)
#######################################################################################################################################################
#######################################################################################################################################################
#######################################################################################################################################################
@app.route('/IndexUyeGiris.html')
def IndexUyeGiris():
     GirisYapanCihazKodu = CihazBilgi.CihazBilgisiOkuma()
     if GirisYapanCihazKodu != '':
          Sifreli = Sifreleme.VeriyiSifrele(GirisYapanCihazKodu)
          User  = SQLServer.Sorgula("SELECT * FROM SKUsers WHERE UserAuth = '" + Sifreli + "'")
          if len(User) > 0:
               if User[0]["IsBlock"]:
                    Mesaj1 = "BLOKELISINIZ"
                    Mesaj2 = "GİRİŞ YAPAMAZSINIZ"
                    return render_template("MsgStop.html", Mesaj1=Mesaj1, Mesaj2=Mesaj2)
               else:
                    UserNo = User[0]["UserID"] 
                    GirisNo = AnaSayfaIlkGirisi(UserNo)
                    if GirisNo == 0:
                         global AdminUlasim
                         AdminUlasim=True
                         global UserUlasim
                         UserUlasim=False
                         return redirect("/AdmKullanicilar")
                    elif GirisNo == 1:
                         AdminUlasim=False
                         UserUlasim=True
                         return render_template('User.html', SiteSahibi=SiteSahibi, Unvan=Unvan, ClientAdi=ClientAdi)
                    else:
                         return render_template('UyeGiris.html')
          else:
               return render_template('UyeGiris.html')
     else:
          return redirect('index.html')
#######################################################################################################################################################
#######################################################################################################################################################
#######################################################################################################################################################
@app.route('/ButunModeller.html')
def ButunModeller():
    session['ModelID'] = "0"
    return redirect("/ButunModeller")

@app.route('/ModelSorgulama/<string:ModelID>')
def GrupModelleri(ModelID):
      # Assuming ModelSorgula is properly defined
    session['ModelID'] = str(ModelID)
    return redirect("/ButunModeller")

@app.route("/ButunModeller", methods=["GET"])
def SANALBUTUNMODELLER():
     ModelID = int(session.get('ModelID'))
     if ModelID==0:
          ModelID = random.randint(101, 105)
     SQLGrublar = "SELECT * FROM SKGroups WHERE GrubID IN (SELECT GrubID FROM SKModels) ORDER BY GrubID"
     Groups = SQLServer.Sorgula(SQLGrublar)  
     Models = ModelSorgula(ModelID)
     return render_template('ButunModeller.html', SiteSahibi=SiteSahibi, Unvan=Unvan, ClientAdi=ClientAdi, Groups=Groups, Models=Models)
#######################################################################################################################################################
#######################################################################################################################################################
#######################################################################################################################################################
@app.route('/Sosyal.html')
def Sosyal():
     return render_template('Sosyal.html', SiteSahibi=SiteSahibi, Unvan=Unvan, ClientAdi=ClientAdi)
#######################################################################################################################################################
#######################################################################################################################################################
#######################################################################################################################################################
@app.route('/UyeOlun.html')
def UyeOlun():
     Mesaj=""
     return render_template('UyeOlun.html', Mesaj = Mesaj)
#######################################################################################################################################################
#######################################################################################################################################################
#######################################################################################################################################################
@app.route('/KullanimSartlari.html')
def KullanimSartlari():
     APaket = SQLServer.Sorgula("SELECT * FROM SKPaketler ORDER BY ID")
     return render_template('KullanimSartlari.html', SiteSahibi=SiteSahibi, Unvan=Unvan, ClientAdi=ClientAdi, AbonelikPaket=IndexYorum.APaket)
     
#######################################################################################################################################################
#######################################################################################################################################################
#######################################################################################################################################################
@app.route('/UyeGirisSonKontroller', methods=["POST"] )
def SonKontrolYorumlar():
     GirisMusaade = False
     GirisYapanCihazKodu =  CihazBilgi.CihazBilgisiOkuma()
     if GirisYapanCihazKodu != '':
          MailAdres     = request.form.get("MailAdres")
          UserName      = request.form.get("UserName")
          UserPass      = request.form.get("PassWord")
          OnayKodu      = request.form.get("OnayKodu")
          Durum = MailAdres is not None
          Durum = Durum and UserName is not None
          Durum = Durum and UserPass is not None
          Durum = Durum and OnayKodu is not None
          
          if Durum:
               UserPass      = Sifreleme.VeriyiSifrele(UserPass)
               SifreliCihaz  = Sifreleme.VeriyiSifrele(GirisYapanCihazKodu)
               AnaSorgu=f"RTRIM(UserName)='{UserName}' AND RTRIM(PassWord)='{UserPass}' AND RTRIM(UserMailAdress)='{MailAdres}'"
               
               PasswKontrol1 = SQLServer.Sorgula(f"SELECT * FROM SKUsers WHERE {AnaSorgu}") 
               CihazKontrol2 = SQLServer.Sorgula(f"SELECT * FROM SKUsers WHERE {AnaSorgu} AND RTRIM(UserAuth)='{SifreliCihaz}'") 

               if len(PasswKontrol1) == 1 and len(CihazKontrol2) == 1:
                    if not(PasswKontrol1[0]["IsBlock"]):
                         # Kullanıcı Adı ve Şifresi ve Cihaz Numarası Uyuştu. Daha  Önce Bu Cihazla Girdiğinden Atlıyoruz.
                         GirisMusaade=True
                    else:
                         Mesaj1 = "BLOKELISINIZ"
                         Mesaj2 = "GİRİŞ YAPAMAZSINIZ"
                         return render_template("MsgStop.html", Mesaj1=Mesaj1, Mesaj2=Mesaj2)
               elif len(PasswKontrol1) == 0:
                    # Kullanıcı Adı ve Şifresi Uyuşmadı
                    Mesaj1 = "HATALI BİLGİ GİRİŞİ"
                    Mesaj2 = "eMail, KullanıcıAdı, Şifre ve OnayKodu Uyuşmamıştır"
                    return render_template("MsgStop.html", Mesaj1=Mesaj1, Mesaj2=Mesaj2)
               elif len(PasswKontrol1) == 1 and len(CihazKontrol2) == 0:
                    UserAuth = PasswKontrol1[0]["UserAuth"]
                    if UserAuth.strip() > "":
                         if PasswKontrol1[0]["IsBlock"] == False:
                              ## Yetkisiz Giriş Algılandı Bloke Edip Aboneliğini İptal Edeceğiz....
                              TarihZaman = datetime.now()
                              formatli_tarih = TarihZaman.strftime("%d.%m.%Y %H.%M.%S.%f")
                              #Kullanıcıya Mail Gidiyor
                              #Kullanıcıya Mail Gidiyor
                              #Kullanıcıya Mail Gidiyor
                              MailAdres = PasswKontrol1[0]["UserMailAdress"]
                              Baslik    = "Yetkisiz Cihazla Giriş Algılandı..."
                              Konu      = "Kayıtlı bulunan cihaz haricinde başka bir cihazla girişiniz algılandı...\n\n"
                              Konu     += "Sözleşme Şartları gereğince üyeliğiniz iptal edilmiştir.\n\n"
                              Konu     += F"Tarih/Saat :{formatli_tarih}"
                              MailGonder.MailGonderme(MailAdres, Baslik, Konu)
                         
                              #Admin'e Mail Gidiyor
                              #Admin'e Mail Gidiyor
                              #Admin'e Mail Gidiyor
                              Baslik    ="Kullanıcı Kaçak Girişi Algılandı ve Bloke Edildi..."
                              Konu      = "Aşağıdaki Kullanıcının Kayıtlı bulunan cihaz haricinde başka bir cihazla giriş algılandı...\n\n"
                              Konu     += "Sözleşme Şartları gereğince üyeliği iptal edilerek blokaj konulmuştur.\n\n"
                              Konu     += "Bu üyenin mail adresi ve telefon numarası kara listede saklanmaya devam edecektir.\n\n"
                              
                              Konu     += F"Kullanıcının Adı Soyadı: {PasswKontrol1[0]["UserAdiSoyadi"].strip()}\n"
                              Konu     += F"Kullanıcının UserName: {PasswKontrol1[0]["UserName"].strip()}\n"
                              Konu     += F"Kullanıcının GSM Numarası: {PasswKontrol1[0]["UserGSMNumber"].strip()}\n"
                              Konu     += F"Kullanıcının Mail Adresi: {PasswKontrol1[0]["UserMailAdress"].strip()}\n"
                              Konu     += F"Kullanıcının Üyelik Tarihi: {PasswKontrol1[0]["UyelikTalepTarihi"].strftime("%d.%m.%Y %H.%M.%S.%f")}\n"
                              Konu     += F"Kullanıcının Üyelik Paketi: {PasswKontrol1[0]["PaketAdi"].strip()}\n"
                              Konu     += F"Kullanıcının Üyelik Onay Tarihi: {PasswKontrol1[0]["UyelikOnayTarihi"].strftime("%d.%m.%Y %H.%M.%S.%f")}\n"
                              Konu     += F"Blokaj Tarihi: {formatli_tarih}\n"
                              MailGonder.MailGonderme(IndexYorum.WSabit[0]["Sutun08"], Baslik, Konu)

                              max_deneme = 50
                              deneme = 0

                              while deneme < max_deneme:
                                   try:
                                        SQLServer.Calistir(f"UPDATE SKUsers SET IsBlock=1, BlockTarihi='{TarihZaman}', OnOff=0 WHERE UserID={PasswKontrol1[0]["UserID"]}")
                                   except Exception as e:
                                        deneme += 1
                                        time.sleep(1)  
                                   else:
                                        break

                         return render_template('MsgBlocked.html')
                    else:
                         GirisMusaade=True
                        
          else:
               Mesaj1="Ooops!!!"
               Mesaj2="Bütün Satırları Doldurmalısınız"
               return render_template('MsgStop.html', Mesaj1 = Mesaj1, Mesaj2=Mesaj2)
     else:
          Mesaj1="Ooops!!!"
          Mesaj2="Cihazınız Bilgilerine Erişim İzni Vermelisiniz"
          return render_template('MsgStop.html', Mesaj1 = Mesaj1, Mesaj2=Mesaj2)
     
     if GirisMusaade:
          SQLServer.Calistir(f"Update SKUsers SET UserAuth='{SifreliCihaz}', OnOff = 1 WHERE UserID={PasswKontrol1[0]["UserID"]}")
          SayfaUserID = PasswKontrol1[0]["UserID"]
          GirisNo     = AnaSayfaIlkGirisi(SayfaUserID)
          global AdminUlasim
          global UserUlasim
          if GirisNo == 0:
               AdminUlasim=True
               UserUlasim=False
               return redirect("/AdmKullanicilar")
          elif GirisNo == 1:
               AdminUlasim = False
               UserUlasim  = True
               return render_template('User.html',SiteSahibi=SiteSahibi, Unvan=Unvan, ClientAdi=ClientAdi)
          else:
               AdminUlasim = False
               UserUlasim  = False
               return render_template('UyeGiris.html')
#######################################################################################################################################################
#######################################################################################################################################################
#######################################################################################################################################################
def AnaSayfaIlkGirisi(UserID):
     global ClientAdi
     ClientAdi=""
     if UserID > 0:
          PasswKontrol1 = SQLServer.Sorgula(f"SELECT * FROM SKUsers WHERE UserID={UserID}") 
          ClientAdi=PasswKontrol1[0]["UserAdiSoyadi"]
          if PasswKontrol1[0]["IsAdmin"]:
               return 0
          elif PasswKontrol1[0]["OnOff"]:
               return 1
          else:
               return 2
     else:
          return 2
#######################################################################################################################################################
#######################################################################################################################################################
#######################################################################################################################################################
@app.route(f'/AdmUyeKapat/<string:session_id>/<string:UserID>', methods=["POST"])
def AdmUyePasifleme(session_id, UserID):
     if AdminUlasim and session_id==SessionID:
          session['UserID'] = UserID
          GuncelTarih =str(datetime.now().strftime('%Y-%m-%d'))
          SqlKomutu=f"UPDATE SKUsers SET OnOff = 0 WHERE UserID = {UserID}"
          Durum1 = SQLServer.Calistir(SqlKomutu)
          #Kullanıcıya Üyeliğiniz Kapatıldı Bilgisini Verelim...
          if Durum1:
               User = SQLServer.Sorgula(f"SELECT * FROM SKUsers WHERE UserID={UserID}")
               SQLMemberDateID = User[0]["SQLMemberDateID"]
               GuncelTarih =str(datetime.now().strftime('%Y-%m-%d'))
               SqlKomutu = f"UPDATE SKMemberDates SET SonlanmaTarihi='{GuncelTarih}' WHERE UserID={UserID} AND ID={SQLMemberDateID}"     
               Durum2 = SQLServer.Calistir(SqlKomutu)
               if Durum2:
                    Baslik = "Serap KOÇAK Web Sitesi Bilgilendirme"
                    Mesaj  =  f"Sayın: {User[0]["UserAdiSoyadi"].strip()}\n\n"
                    Mesaj +=  f"Serap KOÇAK Web Sitesi'nde Yeni Projelere Erişiminiz Kapatılmıştır.\n\n"
                    Mesaj +=  f"Üyeliğinizin aktif olduğu tarihler arasında yayınlanan projelere erişiminiz açıktır."
                    MailGonder.MailGonderme(User[0]["UserMailAdress"].strip(),Baslik, Mesaj)
          return redirect("/AdmKullanicilar")
     else:
          return "<h1>Yetkisiz Ulaşım"

@app.route(f'/AdmUyeAktifle/<string:session_id>/<string:UserID>/<string:PaketID>', methods=["POST"])
def AdmUyeAktifleme(session_id, UserID, PaketID):
     if AdminUlasim and session_id==SessionID:
          session['UserID'] = UserID 
          GuncelTarih =str(datetime.now().strftime('%Y-%m-%d'))
          SqlKomutu = f"INSERT INTO SKMemberDates (UserID, BaslamaTarihi, SonlanmaTarihi) VALUES ({UserID}, '{GuncelTarih}', NULL)"
          SQLMemberDateID = SQLServer.IdentityCalistir(SqlKomutu)
          PaketCinsi = ""
          if PaketID=="1":
               PaketCinsi="WS"
          elif PaketID=="2":
               PaketCinsi="MP"
          elif PaketID=="0":
               PaketCinsi="SP"
          SqlKomutu=f"UPDATE SKUsers SET SQLMemberDateID={SQLMemberDateID}, OnOff = 1, PaketAdi='{PaketCinsi}' WHERE UserID = {UserID}"
          Durum2 = SQLServer.Calistir(SqlKomutu)

          #Kullanıcıya Üyeliğiniz Açıldı Bilgisi Verelim...
          if SQLMemberDateID > 0 and Durum2:
               User = SQLServer.Sorgula(f"SELECT * FROM SKUsers WHERE UserID={UserID}")
               Baslik = "Serap KOÇAK Web Sitesi Bilgilendirme"
               Mesaj  = f"Sayın: {User[0]["UserAdiSoyadi"].strip()}\n\n"
               Mesaj +=  f"Serap KOÇAK Web Sitesine Erişiminiz İçin Site Giriş Bilgileriniz Aşağıda Sunulmuştur...\n\n\n"
               Mesaj += f"Adınız Soyadınız: {User[0]["UserAdiSoyadi"].strip()}\n"
               Mesaj += f"Mail Adresiniz: { User[0]["UserMailAdress"].strip()}\n"
               Mesaj += f"Şifreniz: { Sifreleme.VeriyiCoz(User[0]["PassWord"].strip()) }\n"
               Mesaj += f"Onay Kodunuz: {User[0]["VerifyMailCode"]}\n\n\n"
               Mesaj += f"İlk Giriş Yaptığınızda Kullandığınız Cihaz Bilgileri Sistemimizde Kayıt Edilecek Olup, "
               Mesaj += f"Tekrar sisteme başka bir cihazla giriş yaparsanız üyeliğinizin iptal edileceğini, "
               Mesaj += f"SİTE KULLANIM KURALLARI gereğince önemle hatırlatırız."
               MailGonder.MailGonderme(User[0]["UserMailAdress"].strip(),Baslik, Mesaj)
          return redirect("/AdmKullanicilar")
     else:
          return "<h1>Yetkisiz Ulaşım"

@app.route("/AdmKullanicilar", methods=["GET"])
def SANALADMKULLANICILAR():
     global AdminUlasim
     global UserUlasim
     if AdminUlasim:
          UserID = session.get('UserID')
          Sql  = "SELECT (SELECT BaslamaTarihi from SKMemberDates WHERE SKMemberDates.ID=SKUsers.SQLmemberDateID) AS BaslamaTarihi, "
          Sql += " (SELECT SonlanmaTarihi from SKMemberDates WHERE SKMemberDates.ID=SKUsers.SQLmemberDateID) AS SonlanmaTarihi, "
          Sql += "SKUsers.* FROM SKUsers ORDER BY UserAdiSoyadi"
          Users = SQLServer.Sorgula(Sql)
          if len(Users)>0:
               for User in Users:
                    UTalep   = Formatlama.TarihToString(User["UyelikTalepTarihi"], False)
                    UBaslama = Formatlama.TarihToString(User["BaslamaTarihi"], False)
                    UAyrilma = Formatlama.TarihToString(User["SonlanmaTarihi"], False)
                    UBloke   = Formatlama.TarihToString(User["BlockTarihi"], False)
                    UPaket   = User["PaketAdi"].strip()
                    IsAdmin  = User["IsAdmin"]

                    Mesaj=f"UTalep: {UTalep} / UOnay: {UBaslama} / UAyrilma: {UAyrilma} / UBloke: {UBloke} / Paket:"

                    if UBloke != "-----":
                         DRM = "BLOKE EDİLDİ"
                    else:
                         if UAyrilma == "-----" and UBaslama == "-----":
                              DRM = "ÖDEME BEKLENİYOR"
                         elif UAyrilma == "-----" and UBaslama != "-----":
                              if IsAdmin and UPaket=="ADMIN":
                                   DRM="YÖNETİCİ"
                              else:
                                   DRM = "AKTİF"
                         elif UAyrilma != "-----" and UBaslama == "-----":
                              DRM = "RED EDİLDİ"
                         elif UAyrilma != "-----" and UBaslama != "-----":
                              DRM = "PASİF"
                    User["UTalep"]   = UTalep
                    User["UOnay"]    = UBaslama
                    User["UAyrilma"] = UAyrilma
                    User["UBloke"]   = UBloke
                    User["DRM"]      = DRM
               return render_template("AdmKullanicilar.html",SiteSahibi=SiteSahibi, Unvan=Unvan, Users=Users, ClientAdi=ClientAdi, SessionID = SessionID)
     else:
          return "<h1>Yetkisiz Ulaşım"

#######################################################################################################################################################
#######################################################################################################################################################
#######################################################################################################################################################
@app.route('/AdmModelAc/<string:session_id>/<string:id>', methods=["POST"])
def AdmModelAc(session_id, id):
    if AdminUlasim and SessionID==session_id:
        session['UserID'] = id  # UserID'yi oturumda saklıyoruz.
        session['IlkSatir'] = 1
        session['SonSatir'] = 10
        return redirect("/AdmModelAcKapat")
    else:
        return "<h1>Yetkisiz Ulaşım</h1>"
    

@app.route('/ModelAcmaSonraki/<string:session_id>/<string:SonSatir>/', methods=["POST"])
def AdmModelSonraki(session_id, SonSatir):
     if AdminUlasim and session_id==SessionID:
          session['IlkSatir'] = str(int(SonSatir) + 1)  # SonSatir'i integer'a dönüştür
          session['SonSatir'] = str(int(SonSatir) + 10)  # SonSatir'i integer'a dönüştür
          return redirect("/AdmModelAcKapat")
     else:
          return "<h1>Yetkisiz Ulaşım</h1>"
     

@app.route('/ModelAcmaOnceki/<string:session_id>/<string:IlkSatir>/', methods=["POST"])
def AdmModelOnceki(session_id, IlkSatir):
     if AdminUlasim and session_id==SessionID:
          session['SonSatir'] = str(int(IlkSatir) - 1)  # SonSatir'i integer'a dönüştür
          session['IlkSatir'] = str(int(IlkSatir) - 10)  # SonSatir'i integer'a dönüştür
          return redirect("/AdmModelAcKapat")
     else:
          return "<h1>Yetkisiz Ulaşım</h1>"
     
@app.route("/AdmModelAcKapat", methods=["GET"])
def SANALMODELACMA():
     global AdminUlasim
     global UserUlasim
     if AdminUlasim:
          UserID     = int(session.get('UserID'))
          IlkSatir   = int(session.get('IlkSatir'))
          SonSatir   = int(session.get('SonSatir'))
          if int(IlkSatir)<1:
               IlkSatir=1
               SonSatir=10
          
          ModelSys = SQLServer.DegerGetir("SELECT COUNT(*) FROM SKModels")
          if int(ModelSys)<SonSatir:
               SonSatir=int(ModelSys)

          Models = AdminModelAcma.ModelAcmaGirisi(UserID, IlkSatir, SonSatir)
          UserAdiSoyadi  = SQLServer.Sorgula(f"SELECT UserAdiSoyadi FROM SKUsers WHERE UserID = {UserID}")

          return render_template("AdmModelAcKapat.html",SiteSahibi=SiteSahibi, Unvan=Unvan, Models = Models, SessionID = SessionID, UserAdiSoyadi = UserAdiSoyadi, IlkSatir=IlkSatir, SonSatir=SonSatir, ToplamSatir=ModelSys)
     else:
          return "<h1>Yetkisiz Ulaşım"
#######################################################################################################################################################
#######################################################################################################################################################
#######################################################################################################################################################
@app.route("/AdmWebAyarlari")
def SANALWEBAYARLARI():
     global AdminUlasim
     if AdminUlasim:
          WebSabitler=SQLServer.Sorgula("SELECT * FROM SkWebSabitler")
          Paketler=SQLServer.Sorgula("SELECT * FROM SKPaketler")
          return render_template("AdmWebAyar.html", SiteSahibi=SiteSahibi, Unvan=Unvan, ClientAdi=ClientAdi, WebSabitler = WebSabitler, Paketler = Paketler)
     else:
          return "<h1>Yetkisiz Ulaşım"
     
@app.route('/AdmWEBKaydet', methods=["POST"])
def AdmWEBKaydet():
     global AdminUlasim
     if AdminUlasim:
          Sutun1  = request.form.get('AdSoyad')
          Sutun2  = request.form.get('Unvan')
          Sutun3  = request.form.get('Slogan')
          Sutun4  = request.form.get('Aciklama1')
          Sutun5  = request.form.get('Aciklama2')
          Sutun6  = request.form.get('Aciklama3')
          Sutun7  = request.form.get('Aciklama4')
          Sutun8  = request.form.get('email')
          Sutun9  = request.form.get('Adres')
          Sutun10 = request.form.get('Telefon')
          SQLUpd1  = f"Sutun01='{Sutun1}', "
          SQLUpd1 += f"Sutun02='{Sutun2}', "
          SQLUpd1 += f"Sutun03='{Sutun3}', "
          SQLUpd1 += f"Sutun04='{Sutun4}', "
          SQLUpd1 += f"Sutun05='{Sutun5}', "
          SQLUpd1 += f"Sutun06='{Sutun6}', "
          SQLUpd1 += f"Sutun07='{Sutun7}', "
          SQLUpd1 += f"Sutun08='{Sutun8}', "
          SQLUpd1 += f"Sutun09='{Sutun9}', "
          SQLUpd1 += f"Sutun10='{Sutun10}'"
          SQLUpd1  = f"UPDATE SKWebSabitler SET {SQLUpd1} WHERE HTMLSayfaAdi LIKE 'Index%'"

          Cins    = request.form.get('WSAciklamaCins')
          Sutun1  = request.form.get('WSAciklama1')
          Sutun2  = request.form.get('WSAciklama2')
          Sutun3  = request.form.get('WSAciklama3')
          Sutun4  = request.form.get('WSAciklama4')
          SutunF  = request.form.get('WSAciklamaSutunFiyat')
          Kural   = request.form.get('KKWSAciklama')
          SQLUpd2 = f"Cins='{Cins}', Sutun1='{Sutun1}', Sutun2='{Sutun2}', Sutun3='{Sutun3}', Sutun4='{Sutun4}', SutunFiyat='{SutunF}', Kurallar='{Kural}'"
          SQLUpd2 = f"UPDATE SKPaketler SET {SQLUpd2} WHERE ID=11"
          

          Cins    = request.form.get('MPAciklamaCins')
          Sutun1  = request.form.get('MPAciklama1')
          Sutun2  = request.form.get('MPAciklama2')
          Sutun3  = request.form.get('MPAciklama3')
          Sutun4  = request.form.get('MPAciklama4')
          SutunF  = request.form.get('MPAciklamaSutunFiyat')
          Kural   = request.form.get('KKMPAciklama')
          SQLUpd3 = f"Cins='{Cins}', Sutun1='{Sutun1}', Sutun2='{Sutun2}', Sutun3='{Sutun3}', Sutun4='{Sutun4}', SutunFiyat='{SutunF}', Kurallar='{Kural}'"
          SQLUpd3 = f"UPDATE SKPaketler SET {SQLUpd3} WHERE ID=12"
          
          Cins    = request.form.get('SPAciklamaCins')
          Sutun1  = request.form.get('SPAciklama1')
          Sutun2  = request.form.get('SPAciklama2')
          Sutun3  = request.form.get('SPAciklama3')
          Sutun4  = request.form.get('SPAciklama4')
          SutunF  = request.form.get('SPAciklamaSutunFiyat')
          Kural   = request.form.get('KKSPAciklama')
          SQLUpd4 = f"Cins='{Cins}', Sutun1='{Sutun1}', Sutun2='{Sutun2}', Sutun3='{Sutun3}', Sutun4='{Sutun4}', SutunFiyat='{SutunF}', Kurallar='{Kural}'"
          SQLUpd4 = f"UPDATE SKPaketler SET {SQLUpd4} WHERE ID=13"
          SQLServer.Calistir(SQLUpd1)
          SQLServer.Calistir(SQLUpd2)
          SQLServer.Calistir(SQLUpd3)
          SQLServer.Calistir(SQLUpd4)
          return redirect("/AdmWebAyarlari")
     else:
          return "<h1>Yetkisiz Ulaşım"
#######################################################################################################################################################
#######################################################################################################################################################
#######################################################################################################################################################

if __name__ == '__main__':
    # app.run(ssl_context='adhoc', debug=True)
    app.run(debug=True)
    Gecici = 1

