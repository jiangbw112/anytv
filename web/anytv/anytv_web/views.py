from django.shortcuts import render
from anytv_web.models import LiveInfo
from django.core.paginator import Paginator
# Create your views here.
tv_cate={'all':'all',
         'war3':'魔兽争霸',
         'overwatch':'守望先锋',
         'sc2':'星际争霸',
         'hots':'风暴英雄',
         'how':'炉石传说'
         }
def get_one_cate(collection,cate):
    if cate=='all':
        pipeline = [
            {'$sort':{'ob_num':-1}}
        ]
    else:
        pipeline = [
            {'$match':{'tag':cate}},
            {'$sort':{'ob_num':-1}}
        ]
    object_list=[i for i in collection._get_collection().aggregate(pipeline)]
    return object_list

def cate_index():
    pass

def index(request):
    # live_info = LiveInfo.objects


    page = request.GET.get('page',1)
    cate = request.GET.get('cate','all')
    search = request.GET.get('search','none')
    if search=='none':
        live_info=get_one_cate(LiveInfo,tv_cate[cate])
    else:
        # live_info=LiveInfo.objects(owner=search)
        live_info=LiveInfo._get_collection().find({'owner':{'$regex':'.*'+search+'.*'}})

    paginator = Paginator(live_info,60)
    items = paginator.page(page)
    item_num=len(list(items))
    content={
        'items':items,
        'item_num':item_num
    }
    return render(request,'index.html',content)


def category(request):
    tv_cate={'war3.jpg':'魔兽争霸',
             'overwatch.jpg':'守望先锋',
             'sc2.jpg':'星际争霸',
             'hos.jpg':'风暴英雄',
             'how.jpg':'炉石传说'}
    # tv_cate=['war3','overwatch','sc2',]
    content={
        'cates':tv_cate
    }
    return render(request,'category.html',content)
