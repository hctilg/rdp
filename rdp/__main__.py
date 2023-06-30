#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# importing the modules
from requests import exceptions as req_exceptions
from telebot import TeleBot as TelegramBotAPI, apihelper
from string import ascii_uppercase, ascii_lowercase, digits
from telebot.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
import screen_brightness_control as sbc
from psutil._common import bytes2human
from pyautogui import screenshot
from datetime import datetime
from random import choices
import subprocess
import pulsectl
import platform
import GPUtil
import psutil
import time
import json
import cv2
import os


class JsonBase():
  
  def __init__(self, file_db: str) :

    try:
      self.file = open(file_db, 'r+')
      
    except FileNotFoundError as ferr : 
      with open(file_db, 'w+') as f:
        f.close()
    
      self.file = open(file_db, 'r+')
    
    except PermissionError as perr:
      quit(perr)
    
    if (self.file.name.split('.')[-1] != 'json'):
      quit(f"[\aErrno 2] No such file or directory: '{str(self.file.name)}'")
    
    self.file_db = self.file.name
    self.file.close()

  def clear(self, backdata: str=''):
    self.write('')

  def write(self,data) :
    with open(self.file_db, 'w+') as f :
      f.write(json.dumps(data))  
      f.close()
  
  def commit(self, data = None) :
    self.data = data if (data!=None) else self.data
    self.write(self.data)

  def get(self, fn = None) :
    with open(self.file_db, 'r+') as f :
      try:
        self.data = json.loads(f.read())
          
      except:
        self.data = []
    
      try:
        fn(data = self.data)
        
      except: ...
    
      f.close()
    
    return(self.data)

def is_token(token: str):
  try:
    TelegramBotAPI(token)\
      .get_me()
    
  except req_exceptions.ConnectTimeout:
    quit("\n  [*] Turn on VPN ! \n")
      
  except req_exceptions.ReadTimeout:
    quit("\n  [*] Turn on VPN ! \n")
    
  except req_exceptions.ConnectionError:
    quit("\n  [*] You're offline :/ \n")
    
  except apihelper.ApiTelegramException:
    return False
  
  return True

def conf_validation():
  db = JsonBase('config.json')
  conf = db.get()

  if type(conf).__name__ == 'dict':  
    if ['token'] == list(conf.keys()):
      if is_token(conf['token']):
        return True

  return False

class Main(TelegramBotAPI):
  def __init__(self):
    db = JsonBase('config.json')
    conf = db.get()
    super().__init__(token=conf['token'], threaded=False, skip_pending=True)
    self.run_sleep = 2
    self.step = 'main'
    self.key = ''.join(choices(ascii_uppercase + ascii_lowercase + digits, k=16))
        
    main_btn = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    main_btn.add('🗂 File Manager', '⚡️ Shell')
    main_btn.add('⚙️ Settings', '📁 Media')
    
    files_btn = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    files_btn.add('📥 Download', '📤 Upload')
    files_btn.add('🛸 Back') 
    
    sets_btn = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    sets_btn.add('☀️ Brightness', '🎚 Volume')
    sets_btn.add('ℹ️ Info', '🛸 Back') 
    
    info_btn = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    info_btn.add('📀 Os', '📡 Network')
    info_btn.add('💽 CPU', '🥏 GPU')
    info_btn.add('💾 Memory', '🗄 Disk')
    info_btn.add('🔋 Battery', '⏰ Local Time')
    info_btn.add('🛸 Back to Settings')
    
    media_btn = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    media_btn.add('📷 Camera', '🖥 ScreenShot', '🛸 Back')
    
    shell_timeout_btn = InlineKeyboardMarkup(row_width=2)
    shell_timeout_btn.add(
      InlineKeyboardButton(text="1 minute", callback_data="shell_timeout_1"),
      InlineKeyboardButton(text="2 minute", callback_data="shell_timeout_2"),
      InlineKeyboardButton(text="3 minute", callback_data="shell_timeout_3"),
      InlineKeyboardButton(text="5 minute", callback_data="shell_timeout_5"),
      InlineKeyboardButton(text="Cancel", callback_data="close")
    )
    
    brightness_btn = InlineKeyboardMarkup(row_width=2)
    brightness_btn.add(
      InlineKeyboardButton(text="➖", callback_data="set_brightness_down"),
      InlineKeyboardButton(text="➕", callback_data="set_brightness_up"),
      InlineKeyboardButton(text="Cancel", callback_data="close")
    )
    
    volume_btn = InlineKeyboardMarkup(row_width=2)
    volume_btn.add(
      InlineKeyboardButton(text="➖", callback_data="set_volume_down"),
      InlineKeyboardButton(text="➕", callback_data="set_volume_up"),
      InlineKeyboardButton(text="Cancel", callback_data="close")
    )
    
    def _back(user_id):
      self.step = 'main'
      try:      
        self.send_message(user_id, "Choose:", reply_markup=main_btn)
        
      except: ...
    
    db = JsonBase('config.json')
    conf = db.get()
    conf_keys = list(conf.keys()) if type(conf).__name__ == 'dict' else []
        
    if 'admin_id' not in conf_keys:
      print(f"  [*] Key: {self.key} \n")
      
    else:
      _back(conf['admin_id'])
    
    @self.callback_query_handler(lambda call: True)
    def process_callback(query):
      data = str(query.data)
      qid = query.id
      msg_id = query.message.id
      user_id = query.from_user.id
      
      if data == 'close':
        self.delete_message(user_id, msg_id)
        self.step = 'main'
      
      elif data.startswith('shell_timeout_'):
        self.delete_message(user_id, msg_id)
        timeout = int(data.split('_')[2])
        self.shell_timeout = timeout
        self.step = 'shell'
        self.send_message(user_id, "Say commands:", reply_markup=ReplyKeyboardRemove(False))
      
      elif data.startswith('set_brightness_'):
        olv = data.split('_')[2] == 'up'
      
        try:
          # get current brightness value
          cbv = sbc.get_brightness()[1]
          if cbv <= 10 and not olv:
            sbc.set_brightness(10)
            self.answer_callback_query(qid, "This is min Brightness!", show_alert=True)
          elif cbv == 100 and olv:
            self.answer_callback_query(qid, "This is max Brightness!", show_alert=True)
          else:
            new_bv = (cbv + 5) if olv else (cbv - 5)
            sbc.set_brightness(new_bv)
            self.edit_message_text(f"Brightness: {new_bv}%", user_id, msg_id, reply_markup=brightness_btn)
      
        except:
          self.answer_callback_query(qid, "Error!", show_alert=True)
          self.delete_message(user_id, msg_id)
        
      elif data.startswith('set_volume_'):
        olv = data.split('_')[2] == 'up'
      
        try:
          with pulsectl.Pulse('volume-increaser') as pulse:
            for sink in pulse.sink_list():
              # get current volume level
              cvl = pulse.volume_get_all_chans(sink)
              is_mute = cvl == 0.0
              
              if not olv and is_mute:
                self.answer_callback_query(qid, "This is min Volume level!", show_alert=True)
              
              elif olv and cvl >= 1.0:
                self.answer_callback_query(qid, "This is max Volume level!", show_alert=True)
              
              else:         
                pulse.volume_change_all_chans(sink, 0.05 if olv else -0.05)
                new_vl = pulse.volume_get_all_chans(sink)
                is_mute = new_vl == 0.0
                vl_text = 'mute' if is_mute else str(int(new_vl * 100)) + '%'
                self.edit_message_text(f"Volume: {vl_text}", user_id, msg_id, reply_markup=volume_btn)
              
            pulse.close()

        except:
          self.answer_callback_query(qid, "Error!", show_alert=True)
          self.delete_message(user_id, msg_id)

    @self.message_handler(content_types=['text', 'video', 'photo', 'audio', 'voice', 'document', 'location'])
    def handler(update):

      text = update.text
      msg_id = update.message_id
      user_id = update.chat.id

      if update.chat.type != 'private':
        return False
      
      db = JsonBase('config.json')
      conf = db.get()
      conf_keys = list(conf.keys()) if type(conf).__name__ == 'dict' else []
      
      if 'admin_id' not in conf_keys:
        if update.content_type == 'text':
          if text == self.key:
            conf['admin_id'] = str(user_id)
            db.commit(conf)
            self.send_message(user_id, "Welcome!")
            self.send_message(user_id, "Choose:", reply_markup=main_btn)
            
      else:
        db = JsonBase('config.json')
        conf = db.get()
        if str(conf['admin_id']) != str(user_id):
          return False
      
      back = lambda : _back(user_id)
      
      if text == '🛸 Back' or text == '/back':
        back()
        return False
            
      if self.step == 'download_file':
        if update.content_type == 'text':
          if os.path.isfile(text):
            file_stat = os.stat(text)
            file_size = file_stat.st_size
            if file_size < (2*10**9):
              file_name = str(text).split('/')[-1]
              self.step = 'main'
              dl_msg = self.send_message(user_id, "Downloading...")
              
              try:
                with open(text, 'rb') as file:
                  self.send_document(user_id, file, visible_file_name=file_name, reply_to_message_id=msg_id)
                  file.close()
              
              except:
                self.send_message(user_id, "Failed to send File", reply_markup=ReplyKeyboardRemove(False), reply_to_message_id=msg_id)
              
              self.delete_message(user_id, dl_msg.message_id)
              self.send_message(user_id, "Choose:", reply_markup=files_btn)
            
            else:
              self.send_message(user_id, "Maximum Size is 2GB !", reply_markup=ReplyKeyboardRemove(False), reply_to_message_id=msg_id)
          
          else:
            self.send_message(user_id, "File Not Found!", reply_markup=ReplyKeyboardRemove(False), reply_to_message_id=msg_id)
            self.send_message(user_id, "File Address?", reply_markup=ReplyKeyboardRemove(False), reply_to_message_id=msg_id)
        
        else:
          self.send_message(user_id, "File Address?", reply_markup=ReplyKeyboardRemove(False), reply_to_message_id=msg_id)
        
        return False
      
      if self.step == 'upload_file':
        if update.content_type == 'document':
          file_name = update.document.file_name
          file_path = self.get_file(update.document.file_id).file_path
          
          current_folder = os.path.dirname(os.path.abspath(__file__))
          desktop_path = current_folder
          
          if os.name == 'nt':  # Windows
            desktop_path = os.path.join(os.environ['USERPROFILE'], 'Desktop')
          
          elif os.name == 'posix':  # MacOS or Linux
            desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
          
          self.step = 'main'
          up_msg = self.send_message(user_id, "Uploading...")
          
          try:
            downloaded_file = self.download_file(file_path)
            new_file_name = f"{desktop_path}/{time.strftime(r'%Y-%m-%d-%H:%M:%S', time.localtime())}-{file_name}"
            with open(new_file_name, 'wb') as new_file:
              new_file.write(downloaded_file)
              new_file.close()
            self.send_message(user_id, f"✅ Uploaded to {new_file_name}", reply_to_message_id=msg_id)
          
          except:
            self.send_message(user_id, "Failed to upload File", reply_markup=ReplyKeyboardRemove(False), reply_to_message_id=msg_id)

          self.delete_message(user_id, up_msg.message_id)
          self.send_message(user_id, "Choose:", reply_markup=files_btn)
        
        else:
          self.send_message(user_id, "Send your File", reply_markup=ReplyKeyboardRemove(False), reply_to_message_id=msg_id)
        
        return False
      
      if self.step == 'shell_get_timeout':
        self.send_message(user_id, "Timeout?", reply_markup=shell_timeout_btn)
        return False
      
      if self.step == 'shell':
        if update.content_type == 'text':
          wait_msg = self.send_message(user_id, 'wait...')       
          
          try:
            ctn = subprocess.Popen(text,
              shell=True,
              universal_newlines=False,
              stdout=subprocess.PIPE,
              stderr=subprocess.PIPE,
              stdin=subprocess.PIPE
            )
            
            STDOUT, STDERR = [str(std.decode('utf-8')) for std in ctn.communicate(input=False, timeout=(self.shell_timeout * 60.0))]
            
            result = str(f"ERROR:\n" + STDERR + "\n" if len(STDERR) > 0 else f"OUTPUT:\n" + STDOUT + "\n")
            
            _filename = ('error' if result.startswith('ERROR') else 'output') + '.txt'
            
            if len(result) < 2500:
              self.send_message(user_id, str(result), reply_to_message_id=msg_id)
            
            else:        
              try:
                with open(_filename, 'w') as file:
                  file.write(result)
                  file.close()
              
                with open(_filename, 'rb') as file:
                  self.send_document(user_id, file, visible_file_name=_filename, reply_to_message_id=msg_id)
                  file.close()
                
                os.remove(_filename)
              
              except:
                self.send_message(user_id, "Failed to send output.", reply_to_message_id=msg_id)
              
          except subprocess.TimeoutExpired:
            self.send_message(user_id, f"Command '{text}' timed out", reply_to_message_id=msg_id)
          
          self.delete_message(user_id, wait_msg.message_id)
          
          back()
          return False
          
        else:
          self.send_message(user_id, "Say commands:", reply_markup=ReplyKeyboardRemove(False))
          
        return False
      
      if update.content_type == 'text':
      
        if text == '🗂 File Manager' or text == '/file_manager':
          self.send_message(user_id, "Choose:", reply_markup=files_btn)
      
        if text == '📥 Download' or text == '/download_file':
          self.step = 'download_file'
          self.send_message(user_id, "File Address?", reply_markup=ReplyKeyboardRemove(False))
      
        if text == '📤 Upload' or text == '/upload_file':
          self.step = 'upload_file'
          self.send_message(user_id, "Send your File", reply_markup=ReplyKeyboardRemove(False))
          
        elif text == '⚡️ Shell' or text == '/shell':
          self.step = 'shell_get_timeout'
          self.send_message(user_id, "Timeout?", reply_markup=shell_timeout_btn)
          
        elif text == '⚙️ Settings' or text == '🛸 Back to Settings' or text == '/settings':
          self.send_message(user_id, "Choose:", reply_markup=sets_btn)
          
        elif text == '☀️ Brightness' or text == '/set_brightness':
          try:
            # get current brightness value
            cbv = sbc.get_brightness()[1]
            self.send_message(user_id, f"Brightness: {cbv}%", reply_markup=brightness_btn, reply_to_message_id=msg_id)
          except:
            self.send_message(user_id, "device doesn't support this feature.", reply_to_message_id=msg_id)
          
        elif text == '🎚 Volume' or text == '/set_volume':
          try:
            with pulsectl.Pulse('volume-increaser') as pulse:
              sink = pulse.sink_list()[0]
              # get current volume level
              cvl = pulse.volume_get_all_chans(sink)
              is_mute = cvl == 0.0
              cvl_text = 'mute' if is_mute else str(int(pulse.volume_get_all_chans(sink) * 100)) + '%'
              self.send_message(user_id, f"Volume: {cvl_text}", reply_markup=volume_btn, reply_to_message_id=msg_id)
              pulse.close()
          except:
            self.send_message(user_id, "device doesn't support this feature.", reply_to_message_id=msg_id)
        
        elif text == 'ℹ️ Info' or text == '/info':
          self.send_message(user_id, "Choose:", reply_markup=info_btn)
        
        # Os information
        elif text == '📀 Os' or text == '/os_info':
          _text = ''
          uname = platform.uname()
          _text += f"System: {uname.system}\n"
          _text += f"Node Name: {uname.node}\n"
          _text += f"Release: {uname.release}\n"
          _text += f"Version: {uname.version}\n"
          _text += f"Machine: {uname.machine}\n"
          if len(uname.processor.strip()) > 0:
            _text += f"Processor: {uname.processor}\n"
          
          boot_time_timestamp = psutil.boot_time()
          bt = datetime.fromtimestamp(boot_time_timestamp)
          _text += f"Boot Time: {bt.year}/{bt.month}/{bt.day} {bt.hour}:{bt.minute}:{bt.second}"
          
          self.send_message(user_id, _text, reply_to_message_id=msg_id)
          
        # Network information
        elif text == '📡 Network' or text == '/network_info':
          _text = ''
          
          # get all network interfaces (virtual and physical)
          if_addrs = psutil.net_if_addrs()

          for interface_name, interface_addresses in if_addrs.items():
            for address in interface_addresses:
              if str(address.family) == 'AddressFamily.AF_INET':
                _title = f"Interface: {interface_name}"
                _text += f'\n{_title}\n' + '=' * (len(_title) + 1) + '\n'
                _text += f"IP Address: {address.address}\n"
                _text += f"Netmask: {address.netmask}\n"
                _text += f"Broadcast IP: {address.broadcast}\n"
              elif str(address.family) == 'AddressFamily.AF_PACKET':
                _title = f"Interface: {interface_name}"
                _text += f'\n{_title}\n' + '=' * (len(_title) + 1) + '\n'
                _text += f"MAC Address: {address.address}\n"
                _text += f"Netmask: {address.netmask}\n"
                _text += f"Broadcast MAC: {address.broadcast}\n"
              
          _text += '\n' + '=' * 30 + '\n'
              
          # get IO statistics since boot
          net_io = psutil.net_io_counters()
          _text += f"Total Bytes Sent: {str(net_io.bytes_sent)}\n"
          _text += f"Total Bytes Received: {str(net_io.bytes_recv)}\n"
          
          self.send_message(user_id, _text, reply_to_message_id=msg_id)
        
        # CPU Details
        elif text == '💽 CPU' or text == '/cpu_details':
          _text = ''

          _title = "number of cores"
          _text += f"\n{_title}\n{'=' * (len(_title) + 1)}\n"
          _text += f"Physical cores: {psutil.cpu_count(logical=False)}\n"
          _text += f"Total cores: {psutil.cpu_count(logical=True)}\n"

          _title = "CPU frequencies"
          _text += f"\n{_title}\n{'=' * (len(_title) + 1)}\n"
          cpufreq = psutil.cpu_freq()
          _text += f"Max Frequency: {cpufreq.max:.2f}Mhz\n"
          _text += f"Min Frequency: {cpufreq.min:.2f}Mhz\n"
          _text += f"Current Frequency: {cpufreq.current:.2f}Mhz\n"

          _title = "CPU Usage Per Core"
          _text += f"\n{_title}\n{'=' * (len(_title) + 1)}\n"
          for i, percentage in enumerate(psutil.cpu_percent(percpu=True, interval=1)):
              _text += f"Core {i}: {percentage}%\n"
              
          _text += f"\nTotal CPU Usage: {psutil.cpu_percent()}%\n"
          
          self.send_message(user_id, _text, reply_to_message_id=msg_id)
        
        # GPU Details
        elif text == '🥏 GPU' or text == '/gpu_details':
          gpus = GPUtil.getGPUs()
          list_gpus, _text = [], ''
          if len(gpus) > 0:
            for gpu in gpus:
              # get the GPU id
              gpu_id = gpu.id
              # name of GPU
              gpu_name = gpu.name
              # get % percentage of GPU usage of that GPU
              gpu_load = f"{gpu.load*100}%"
              # get free memory in MB format
              gpu_free_memory = f"{gpu.memoryFree}MB"
              # get used memory
              gpu_used_memory = f"{gpu.memoryUsed}MB"
              # get total memory
              gpu_total_memory = f"{gpu.memoryTotal}MB"
              # get GPU temperature in Celsius
              gpu_temperature = f"{gpu.temperature} °C"
              gpu_uuid = gpu.uuid
              list_gpus.append({
                "id": gpu_id,
                "name": gpu_name,
                "load": gpu_load,
                "free memory": gpu_free_memory,
                "used memory": gpu_used_memory,
                "total memory": gpu_total_memory,
                "temperature": gpu_temperature,
                "uuid": gpu_uuid
              })
            
            for dict_gpu in list_gpus:
              for key in dict_gpu:
                _text += f"{key}: {list_gpus[key]}\n"
              _text += '\n'
            _text = _text.strip("\n")

          else:
            _text = "GPUs not found."
            
          self.send_message(user_id, _text, reply_to_message_id=msg_id)
        
        # Memory Details
        elif text == '💾 Memory' or text == '/memory_details':
          _text = ''
          
          # get the memory details
          svmem = psutil.virtual_memory()

          _title = "memory details"
          _text += f"\n{_title}\n{'=' * (len(_title) + 1)}\n"
          _text += f"Total: {bytes2human(svmem.total)}\n"
          _text += f"Available: {bytes2human(svmem.available)}\n"
          _text += f"Used: {bytes2human(svmem.used)}\n"
          _text += f"Percentage: {svmem.percent}%\n"

          # get the swap memory details (if exists)
          swap = psutil.swap_memory()
          if len(list(swap)) > 0 :
            _title = "swap memory details"
            _text += f"\n{_title}\n{'=' * (len(_title) + 1)}\n"
            _text += f"Total: {bytes2human(swap.total)}\n"
            _text += f"Free: {bytes2human(swap.free)}\n"
            _text += f"Used: {bytes2human(swap.used)}\n"
            _text += f"Percentage: {swap.percent}%\n"
          
          self.send_message(user_id, _text, reply_to_message_id=msg_id)
        
        # Disk information
        elif text == '🗄 Disk' or text == '/disk_info':
          _text = "Partitions and Usage:\n\n"

          # get all disk partitions
          partitions = psutil.disk_partitions()
          for partition in partitions:
              _title = f"Device: {partition.device}"
              _text += f"\n{_title}\n{'=' * (len(_title) + 1)}\n"
              _text += f"Mountpoint: {partition.mountpoint}\n"
              _text += f"File system type: {partition.fstype}\n"
              try:
                  partition_usage = psutil.disk_usage(partition.mountpoint)
              except PermissionError:
                  # this can be catched due to the disk that
                  # isn't ready
                  continue
              _text += f"Total Size: {partition_usage.total}\n"
              _text += f"Used: {partition_usage.used}\n"
              _text += f"Free: {partition_usage.free}\n"
              _text += f"Percentage: {partition_usage.percent}%\n"

          # get IO statistics since boot
          disk_io = psutil.disk_io_counters()

          _title = 'IO statistics since boot'
          _text += f"\n{_title}\n{'=' * (len(_title) + 1)}\n"
          _text += f"Total read: {bytes2human(disk_io.read_bytes)}\n"
          _text += f"Total write: {bytes2human(disk_io.write_bytes)}\n"
          
          self.send_message(user_id, _text, reply_to_message_id=msg_id)
        
        # Battery information
        elif text == '🔋 Battery' or text == '/battery_info':
          try:
            # function returning time
            def convertTime(seconds):
              minutes, seconds = divmod(seconds, 60)
              hours, minutes = divmod(minutes, 60)
              time_list = ("%d:%02d:%02d" % (hours, minutes, seconds)).split(':')
              return ':'.join(time_list[1:]) + ' (mm:ss)' if int(time_list[0]) == 0 else ':'.join(time_list[:2]) + ' (hh:mm)'
              
            battery, _text = psutil.sensors_battery(), ''
            _text += f"Battery percentage : {str(int(battery.percent))}%\n"
            _text += f"Power plugged in : {str(battery.power_plugged).lower()}\n"
            if not battery.power_plugged:
              _text += f"Battery left : {convertTime(battery.secsleft)}"
            
          except Exception:
            _text = "device doesn't support this feature."
            
          self.send_message(user_id, _text, reply_to_message_id=msg_id)
        
        elif text == '⏰ Local Time' or text == '/time':
          current_time = time.strftime(f"Date: %Y/%m/%d\nClock: %H:%M:%S\nTimeZone: %z", time.localtime())
          self.send_message(user_id, current_time, reply_to_message_id=msg_id)
      
        if text == '📁 Media' or text == '/media':
          self.send_message(user_id, "Choose:", reply_markup=media_btn)
          
        elif text == '📷 Camera' or text == '/cam':

          try:
            # define an object of the VideoCapture class for the camera
            cap = cv2.VideoCapture(0)

            # reading the image from the cam
            ret, frame = cap.read()

            # check image read success
            if ret:
                # save image
                cv2.imwrite(r'captured_image.jpg', frame)

            # close the cam
            cap.release()
            
            with open('captured_image.jpg', 'rb') as file:
              self.send_photo(user_id, file, reply_to_message_id=msg_id)
              os.remove('captured_image.jpg')
              file.close()
              
          except req_exceptions.ConnectTimeout as er:
            raise er
            
          except req_exceptions.ReadTimeout as er:
            raise er
          
          except:
            self.send_message(user_id, "device doesn't support this feature.", reply_to_message_id=msg_id)
        
        elif text == '🖥 ScreenShot' or text == '/screenshot':
          try:
            screenshot()\
              .save('screenshot.png')
            with open('screenshot.png', 'rb') as file:
              self.send_photo(user_id, file, reply_to_message_id=msg_id)
              os.remove('screenshot.png')
              file.close()
          
          except req_exceptions.ConnectTimeout as er:
            raise er
            
          except req_exceptions.ReadTimeout as er:
            raise er
          
          except:
            self.send_message(user_id, "device doesn't support this feature.", reply_to_message_id=msg_id)
        
      else:
        self.send_message(user_id, "Choose:", reply_markup=main_btn)

    self.run()
  
  def run(self):
    error = True
    print("\n  [#] Activated")
    
    try:
      self.polling(none_stop=True)
      error = False
    
    except req_exceptions.ConnectTimeout:
      print("\n  [*] Turn on VPN !")
      
    except req_exceptions.ReadTimeout:
      print("\n  [*] Turn on VPN !")
      
    except req_exceptions.ConnectionError:
      print("\n  [*] You're offline :/")
    
    print('')
    
    if error:
      time.sleep(self.run_sleep)
      self.run_sleep += (1 if self.run_sleep <= 60 else (-1 * self.run_sleep) + 2)
      print("  [#] reActivating...")
      self.run()
  
def get_conf():
  
  db = JsonBase('config.json')
  conf = db.get()
  if type(conf).__name__ != 'dict':
    conf = dict()
    
  conf_keys = list(conf.keys())
  
  token = conf['token'] if 'token' in conf_keys else '74 6F 6B 65 6E'

  while (not is_token(token)):
    token = input("\n  [+] Token: ")
    if not is_token(token):
      print("\n  [!] Token isn't valid :/ ")
  
  conf['token'] = token

  db.commit(conf)

  Main()

if __name__ == '__main__' :          
  try:
    (Main if conf_validation() else get_conf)()
  
  except KeyboardInterrupt:
    quit("\n")
  
  except EOFError:
    quit("\n")