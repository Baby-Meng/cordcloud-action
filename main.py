from string import Template

from actions_toolkit import core

from app import log
from app.action import Action

action = {
    'action': 'CordCloud Action',
    'author': 'Yang Libin',
    'github': 'https://github.com/yanglbme',
    'marketplace': 'https://github.com/marketplace/actions/cordcloud-action'
}

welcome = Template('欢迎使用 $action ❤\n\n📕 入门指南: $marketplace\n📣 由 $author 维护: $github\n')
log.info(welcome.substitute(action))

try:
    # 获取输入
    email = core.get_input('email', required=True)
    passwd = core.get_input('passwd', required=True)
    host = core.get_input('host') or 'cordcloud.us,cordcloud.one,cordcloud.biz,c-cloud.xyz'

    # host 预处理：切分、过滤空值
    hosts = [h for h in host.split(',') if h]

    for i, h in enumerate(hosts):
        # 依次尝试每个 host
        log.info(f'当前尝试 host：{h}')
        action = Action(email, passwd, host=h)
        try:
            # 登录
            res = action.login()
            if res['ret'] != 1:
                log.set_failed(f'CordCloud 帐号登录失败，错误信息：{res}')
            log.info(f'尝试帐号登录，结果：{res}')

            # 签到
            res = action.check_in()
            if res['ret'] != 1 and '您似乎已经签到过' not in res['msg']:
                log.set_failed(f'CordCloud 帐号续命失败，错误信息：{res}')
            msg = '今日签到已完成，不必重复签到' if '您似乎已经签到过' in res['msg'] else f'尝试帐号续命，结果：{res}'
            log.info(msg)

            # 获取流量使用情况
            account = action.info()
            if account:
                today_used, total_used, rest = account
                log.info(f'今日已用：{today_used}, 过去已用：{total_used}, 剩余流量：{rest}')

            # 成功运行，退出循环
            log.info(f'CordCloud Action 成功结束运行！')
            break
        except Exception as e:
            # 失败，尝试下一个 host
            log.warning(f'CordCloud Action 运行异常，错误信息：{str(e)}')
    else:
        # 尝试了所有 hosts，都失败
        log.set_failed(f'CordCloud Action 运行失败！')
except Exception as e:
    log.set_failed(str(e))
