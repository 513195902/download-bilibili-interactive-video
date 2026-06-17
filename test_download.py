import requests

url = "https://upos-sz-estgoss.bilivideo.com/upgcxcode/56/40/127644056/127644056_nb2-1-16.mp4?e=ig8euxZM2rNcNbRVhwdVhwdlhWdVhwdVhoNvNC8BqJIzNbfqXBvEqxTEto8BTrNvN0GvT90W5JZMkX_YN0MvXg8gNEV4NC8xNEV4N03eN0B5tZlqNxTEto8BTrNvNeZVuJ10Kj_g2UB02J0mN0B5tZlqNCNEto8BTrNvNC7MTX502C8f2jmMQJ6mqF2fka1mqx6gqj0eN0B599M=&os=estgoss&og=ali&nbs=1&mid=0&oi=1973051017&platform=pc&gen=playurlv3&deadline=1781692435&trid=5822fcf1e6d849588e6395f8db02a6fu&uipk=5&upsig=c393fead46248103714479f9dcd9da49&uparams=e,os,og,nbs,mid,oi,platform,gen,deadline,trid,uipk&bvc=vod&nettype=0&bw=281886&lrs=-1&buvid=&build=0&dl=0&f=u_0_0&qn_dyeid=68742402cdd8f26a00ab9a806a325bf3&agrr=1&orderid=0,3"

headers = {
    "Referer": "https://www.bilibili.com",
    "User-Agent": "Mozilla/5.0"
}

r = requests.get(
    url,
    headers=headers,
    stream=True
)

with open("test.mp4", "wb") as f:
    for chunk in r.iter_content(8192):
        f.write(chunk)

print("完成")