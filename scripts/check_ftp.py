from ftplib import FTP

filename = "path to file and name to check for like Zip_Codes.zip"

#connect to server
ftp = FTP('<host like gisdata.co.anoka.mn.us')

#provided the server allows anon and passwordless login, login to server
ftp.login() 

listing = ftp.nlst(filename)

if len(listing) == 0:
    print filename, "not found"
elif len(listing) == 1:
    print filename, "ok!"
else:
    print filename, "returned multiple results? Weird..."
