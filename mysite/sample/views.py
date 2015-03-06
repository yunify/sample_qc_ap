from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from sample.control import QcControl
import traceback
from django.views.decorators.clickjacking import xframe_options_exempt
from django.template import RequestContext, loader

user_control={}

# allow post from other site
@csrf_exempt
# allow embedded into iframe
@xframe_options_exempt
def index(request):
    try:
        qc = get_qc(request)
        qc.handle()
        if qc.is_notification:
            return HttpResponse("OK")
        else:
            user = qc.get_user_info()
            user_id = user["user_id"]
            zone = qc.zone
    
            # in real case, you may need to manage user and tokens in database
            # in this example, store them in object for simply
            if user_id not in user_control:
                user_control[user_id] = {}
            if zone not in user_control[user_id]:
                user_control[user_id][zone] = {}
            user_control[user_id][zone]["qc"] = qc
            
            # disable service status for each eip
            eips = qc.get_eips()["eip_set"]
            for eip in eips:
                eip_id = eip["eip_id"]
                if eip["eip_id"] in user_control[user_id][zone] and \
                        user_control[user_id][zone][eip_id]:
                    eip["btn_name"] = "disable"
                else:
                    eip["btn_name"] = "enable"
                
            template = loader.get_template('index.html')
            context = RequestContext(request, {
                'username'    : user['user_name'],
                'user_id'     : user_id,
                'zone'        : zone,
                'notify_email': user['notify_email'],
                'eips'        : eips
            })
            return HttpResponse(template.render(context))
    except Exception:
        exstr = traceback.format_exc()
        print exstr
        return HttpResponse(exstr)

# allow post from other site
@csrf_exempt
def service(request):
    try:
        qc_resource_id = request.POST.get("resource_id")
        appr_id        = request.POST.get("appr_id")
        user_id        = request.POST["user_id"]
        zone           = request.POST["zone"]
        action         = request.POST["action"]
        qc             = user_control[user_id][zone]["qc"]
        if action == "enable":
            # you will need to provide service to your user here
            
            rep = qc.conn.lease_app(settings.SERVICE_ID, qc_resource_id)
            print rep
            if rep:
                appr_id = rep["appr_id"]
                # store appr_id to unlease it later
                user_control[user_id][zone][qc_resource_id] = appr_id
                print "store appr_id %s to qc id %s"%(appr_id, qc_resource_id)
        elif action == "disable":
            # stop your service and then unlease app
    
            # unlease app does not need access_token
            appr_id = user_control[user_id][zone][qc_resource_id]
            print "unlease appr [%s]"%(appr_id)
            if appr_id:
                rep = qc.get_connection(None, zone).unlease_app([appr_id])
                if rep:
                    del user_control[user_id][zone][qc_resource_id]
                print "unlease appr [%s] result is [%s]"%(appr_id, rep)
        else:
            return HttpResponse("not supported action %s"%action)

    except Exception:
        exstr = traceback.format_exc()
        print exstr
        return HttpResponse(exstr)
    return HttpResponse("ok")

def get_qc(request):
    payload   = request.POST["payload"]
    signature = request.POST["signature"]

    return QcControl(payload, signature)