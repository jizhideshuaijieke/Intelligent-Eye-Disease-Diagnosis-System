import smtplib
import logging

from core.config import settings
from email.mime.text import MIMEText
from email.header import Header


class Email:

    @classmethod
    async def sendEmail(self, account: str) -> bool:
        # 邮件内容
        receivers = [account]  # 收件人邮箱地址

        # 邮件内容
        msg = f"""
        尊敬的{receivers[0]},您好！欢迎使用眼科智慧医疗诊断系统。
        您的验证码为：123456
        """
        # 创建邮件对象
        message = MIMEText(msg, "plain", "utf-8")

        # 设置 From 头（发件人名称和邮箱地址）
        from_name = "智慧眼科诊断系统"
        from_email = settings.MAIL_USER
        if all(ord(c) < 128 for c in from_name):
            message["From"] = f"{from_name} <{from_email}>"
        else:
            encoded_name = Header(from_name, "utf-8").encode()  # 对昵称进行 Base64 编码
            message["From"] = f"{encoded_name} <{from_email}>"

        # 设置 To 头（收件人名称和邮箱地址）
        to_name = "使用者"  # 收件人名称（可以是中文）
        to_email = receivers[0]  # 收件人邮箱地址
        if all(ord(c) < 128 for c in to_name):  # 如果昵称是纯 ASCII 字符
            message["To"] = f"{to_name} <{to_email}>"
        else:  # 如果昵称包含非 ASCII 字符（如中文）
            encoded_name = Header(to_name, "utf-8").encode()  # 对昵称进行 Base64 编码
            message["To"] = f"{encoded_name} <{to_email}>"

        message["Subject"] = Header("智慧眼科登录验证码", "utf-8")

        try:
            # 连接 QQ 邮箱的 SMTP 服务器
            smtpObj = smtplib.SMTP_SSL(settings.MAIL_HOST, settings.MAIL_PORT)
            smtpObj.login(settings.MAIL_USER, settings.MAIL_PASSWORD)

            # 发送邮件
            smtpObj.sendmail(settings.MAIL_USER, receivers, message.as_string())
            logging.info(f"邮件发送成功，收件人：{receivers}")
            smtpObj.quit()
            return True
        except smtplib.SMTPException as e:
            logging.error(f"邮件发送失败, 错误信息：{e}")
            smtpObj.quit()
            return False

