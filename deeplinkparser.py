from xml.dom.minidom import parseString
import xml.dom.minidom,os
import subprocess,time,sys


def strdomvalue(name):
	strdata = ''
	with open(out+'/res/values/strings.xml','r',encoding="utf8") as f:
		strdata = f.read()
	strdom = parseString(strdata)
	strings = (strdom.getElementsByTagName('string'))
	for lol in strings :
		for node in (lol.childNodes):
		 	if node.nodeType == node.TEXT_NODE:
		 		if("@string/"+str(lol.attributes["name"].value)==name):
		 			return (node.data)


def deeplink(out):
	data = ''
	with open(out+'/AndroidManifest.xml','r') as f:
	    data = f.read()
	a = []
	b= []
	c= []
	d= []
	e=[]
	i=0;
	dom = parseString(data)
	activities = (dom.getElementsByTagName('activity')+dom.getElementsByTagName('activity-alias'))
	package = (dom.getElementsByTagName('manifest'))
	for lol in package:
		package_name= (lol.attributes["package"].value)

	for activity in activities:
		intentFilterTag = activity.getElementsByTagName("intent-filter")
		if len(intentFilterTag) > 0:
			print("\n----------------------------------------------------------------------------------\n")
			print("\t\t    "+activity.attributes["android:name"].value)
			print("\n----------------------------------------------------------------------------------\n")
			for intent in intentFilterTag:
				dataTag = intent.getElementsByTagName("data")
				if len(dataTag) > 0:
					#print("------------------------------------"+activity.attributes["android:name"].value+"----------------------------------------------\n")

					#calladb(str(activity.attributes["android:name"].value),package_name)
					for data in dataTag:
						if (data.attributes.length==3 and data.hasAttribute("android:pathPrefix")) :
							if "@string" in (str(data.attributes["android:scheme"].value)):
								one=strdomvalue(str(data.attributes["android:scheme"].value))
							else:
								one=str(data.attributes["android:scheme"].value)
							if "@string" in (str(data.attributes["android:host"].value)):
								two=strdomvalue(str(data.attributes["android:host"].value))
							else:
								two=str(data.attributes["android:host"].value)
							if "@string" in (str(data.attributes["android:pathPrefix"].value)):
								three=strdomvalue(str(data.attributes["android:pathPrefix"].value))
							else:
								three=str(data.attributes["android:pathPrefix"].value)
							print(one+"://"+two+three)
							#callhttpdeep(str(one+"://"+two+three),package_name)

						if (data.attributes.length==3 and data.hasAttribute("android:pathPattern")) :
							if "@string" in (str(data.attributes["android:scheme"].value)):
								one=strdomvalue(str(data.attributes["android:scheme"].value))
							else:
								one=str(data.attributes["android:scheme"].value)
							if "@string" in (str(data.attributes["android:host"].value)):
								two=strdomvalue(str(data.attributes["android:host"].value))
							else:
								two=str(data.attributes["android:host"].value)
							if "@string" in (str(data.attributes["android:pathPattern"].value)):
								three=strdomvalue(str(data.attributes["android:pathPattern"].value))
							else:
								three=str(data.attributes["android:pathPattern"].value)
							print(one+"://"+two+three)
						if (data.attributes.length==3 and data.hasAttribute("android:path")) :
							if "@string" in (str(data.attributes["android:scheme"].value)):
								one=strdomvalue(str(data.attributes["android:scheme"].value))
							else:
								one=str(data.attributes["android:scheme"].value)
							if "@string" in (str(data.attributes["android:host"].value)):
								two=strdomvalue(str(data.attributes["android:host"].value))
							else:
								two=str(data.attributes["android:host"].value)
							if "@string" in (str(data.attributes["android:path"].value)):
								three=strdomvalue(str(data.attributes["android:path"].value))
							else:
								three=str(data.attributes["android:path"].value)
							print(one+"://"+two+three)
						if (data.attributes.length==2 and (data.hasAttribute("android:host")and data.hasAttribute("android:scheme"))) :
							if "@string" in (str(data.attributes["android:scheme"].value)):
								one=strdomvalue(str(data.attributes["android:scheme"].value))
							else:
								one=str(data.attributes["android:scheme"].value)
							if "@string" in (str(data.attributes["android:host"].value)):
								two=strdomvalue(str(data.attributes["android:host"].value))
							else:
								two=str(data.attributes["android:host"].value)
							print(one+"://"+two)
							#callhttpdeep(str(one+"://"+two),package_name)

						if (data.attributes.length==1) :
							if data.hasAttribute("android:host") :
								b.append(str(data.attributes["android:host"].value))
							if data.hasAttribute("android:scheme"):
								c.append(str(data.attributes["android:scheme"].value))
							if data.hasAttribute("android:pathPrefix"):
								d.append(str(data.attributes["android:pathPrefix"].value))
							if data.hasAttribute("android:pathPattern"):
								d.append(str(data.attributes["android:pathPattern"].value))
							if data.hasAttribute("android:path"):
								d.append(str(data.attributes["android:path"].value))



				for scheme in c:
					if b==[]:
						if "@string" in (str(scheme)):
								print(strdomvalue(str(scheme))+"://")
						else:
								print(str(scheme)+"://")


					for host in b:
						if d==[]:
							if "@string" in (scheme):
								one=strdomvalue(scheme)
							else:
								one=str(scheme)
							if "@string" in (str(host)):
								two=strdomvalue(str(host))
							else:
								two=str(host)
							print(one+"://"+two)
						for path in d:
							if "@string" in (str(scheme)):
								one=strdomvalue(str(scheme))
							else:
								one=str(scheme)
							if "@string" in (str(host)):
								two=strdomvalue(str(host))
							else:
								two=str(host)
							if "@string" in (path):
								three=strdomvalue(str(path))
							else:
								three=str(path)
							print(one+"://"+two+three)


				a=[]
				b=[]
				c=[]





apk=sys.argv[1]
apk=os.path.basename(apk)
out=apk.rsplit(".",1)[0].replace(' ','_')
cmd="apktool d "+sys.argv[1]+" -o "+out
print(cmd)
os.system(cmd)
deeplink(out)
