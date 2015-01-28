
from django.template import RequestContext, loader
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from sample.control import QcControl
import traceback
from django.views.decorators.clickjacking import xframe_options_exempt

# allow post from other site
@csrf_exempt
# allow embedded into iframe
@xframe_options_exempt
def index(request):
    try:
        qc = get_qc(request)
        user = qc.get_user_info()
        template = loader.get_template('index.html')
        context = RequestContext(request, {
            'username': user['user_set'][0]['user_name'],
            'notify_email': user['user_set'][0]['notify_email'],
        })
        return HttpResponse(template.render(context))
    except Exception:
        exstr = traceback.format_exc()
        print exstr
        return HttpResponse("something wrong")


def get_qc(request):
    payload   = request.POST["payload"]
    signature = request.POST["signature"]

    return QcControl(payload, signature)