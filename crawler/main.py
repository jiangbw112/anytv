from getalltv import init_crawl,get_huya,get_quanmin,get_zhanqi,get_douyu,get_panda,get_douyu_all_info,get_huya_all_info,\
    get_panda_all_info,get_quanmin_all_info,get_zhanqi_all_info,downloadpic,livetbl
import multiprocessing
if __name__ == '__main__':
    init_crawl()

    pool = multiprocessing.Pool()
    multiprocessing.freeze_support()
    pool.map(get_douyu_all_info, get_douyu())
    pool.map(get_quanmin_all_info, get_quanmin())
    pool.map(get_huya_all_info, get_huya())
    pool.map(get_zhanqi_all_info, get_zhanqi())
    pool.map(get_panda_all_info, get_panda())

    for i in livetbl.find():
        pool.apply_async(downloadpic,args=(i['room_imgsrc'],i['room_pic'],))
    pool.close()
    pool.join()