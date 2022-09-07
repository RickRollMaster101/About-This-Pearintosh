#!/usr/bin/python3
from operator import sub
import webbrowser
import subprocess
from typing import OrderedDict
import gi, json, os, subprocess, re, sys, shutil
from numpy import fix
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GdkPixbuf, Gdk

SCRIPTDIR = os.path.dirname(os.path.realpath(__file__))
DEFAULT_OV_CONF = SCRIPTDIR + "/overview-conf.json"

def show_error(maintext, secondarytext):
    print(maintext, ":", secondarytext)
    dialog = Gtk.MessageDialog(
        flags=0,
        message_type=Gtk.MessageType.ERROR,
        buttons=Gtk.ButtonsType.OK,
        text=maintext 
    )
    dialog.format_secondary_text(secondarytext)
    dialog.run()
    dialog.destroy()

class MainWindow(Gtk.Window):
    def __init__(self, overview_json_path=DEFAULT_OV_CONF):
        Gtk.Window.__init__(self, title="About this PC")
        self.set_resizable(False)
        
        # Add a custom headerbar
        self.hb = Gtk.HeaderBar()
        self.hb.props.show_close_button = True
        self.set_titlebar(self.hb)

        # Add a stack and stack switcher
        self.stack = Gtk.Stack()
        self.add(self.stack)
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.stack.set_transition_duration(500)

        self.stack_sw = Gtk.StackSwitcher()
        self.stack_sw.set_stack(self.stack)
        self.hb.set_custom_title(self.stack_sw)

        # Initialize the "Overview" tab
        self.overview_json_path = overview_json_path
        self.overview_init()
        
        # Initialize the "Displays" tab
        self.display_init()
        # Initialize the "Storage" tab
        self.storage_init()
        # Initialize the "Support" tab
        self.support_init()
        # Initialize the "Service" tab
        self.service_init()

    def overview_init(self):
        # Load information from json
        print("Loading config from", self.overview_json_path)
        with open(self.overview_json_path, mode="rt") as f:
            conf = json.loads(f.read())
        
        if not validate_overview_json(self.overview_json_path):
            sys.exit(-1)

        # Horizontal box (2 col: distro image and info)
        overview_layout = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=conf["logo_space"])
        self.stack.add_titled(overview_layout, "overview_layout", "Overview")

        # Vert box (3 rows: distro_info, system_info, addi_btn)
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=conf["section_space"])
        
        distro_info =  Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        system_info = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        addi_btn = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

        # Set alignments
        distro_info.props.halign = system_info.props.halign = addi_btn.props.halign = Gtk.Align.START

        # Initialize distro info
        distro_name = Gtk.Label()
        distro_name.set_markup(conf["distro_markup"])
        distro_name.props.halign = Gtk.Align.START

        distro_ver = Gtk.Label(label=conf["distro_ver"])
        distro_ver.props.halign = Gtk.Align.START

        distro_info.pack_start(distro_name, False, False, 0)
        distro_info.pack_start(distro_ver, False, False, 0)

        # Initialize system info
        FIELD_SP = 20
        hostname = Gtk.Label()
        hostname.set_markup(f"<span font_weight='bold'>{conf['hostname']}</span>")
        hostname.props.halign = Gtk.Align.START
        system_info.pack_start(hostname, False, False, 0)

        info_dict = {"Processor": conf["cpu"], "Memory": conf["memory"], "Startup Disk": conf["startup_disk"], "Graphics": conf["graphics"], "Serial Number": conf["serial_num"]}
        for key in info_dict:
            line = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=FIELD_SP)

            property_name = Gtk.Label()
            property_name.set_markup(f"<span font_weight='bold'>{key}</span>")
            property_name.props.halign = Gtk.Align.START

            line.pack_start(property_name, False, False, 0)
            line.pack_start(Gtk.Label(label=info_dict[key]), False, False, 0)
            line.props.halign = Gtk.Align.START
            system_info.pack_start(line, False, False, 0)
        
        # Initialize additional buttons
        sys_report_btn = Gtk.Button(label="System Report...")
        software_upd_btn = Gtk.Button(label="Software Update...")
        addi_btn.pack_start(sys_report_btn, False, False, 0)
        addi_btn.pack_start(software_upd_btn, False, False, 0)

        # Pack distro_info, system_info, addi_btn into vbox
        vbox.pack_start(distro_info, True, True, 0)
        vbox.pack_start(system_info, True, True, 0)
        vbox.pack_start(addi_btn, True, True, 0)

        # Intialize distro image
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            filename=conf["distro_image_path"], 
            width=conf["distro_image_size"][0], 
            height=conf["distro_image_size"][1], 
            preserve_aspect_ratio=True)

        distro_img = Gtk.Image.new_from_pixbuf(pixbuf)

        overview_layout.pack_start(distro_img, True, True, 0)
        overview_layout.pack_start(vbox, True, True, 0)

        overview_layout.props.margin_start = conf["overview_margins"][0]
        overview_layout.props.margin_end = conf["overview_margins"][1]
        overview_layout.props.margin_top = conf["overview_margins"][2]
        overview_layout.props.margin_bottom = conf["overview_margins"][3]
    
    def display_init(self):
        with open(self.overview_json_path, mode="rt") as f:
            conf = json.loads(f.read())

        fixed = Gtk.Fixed()

        # Add the "Display" tab
        self.stack.add_titled(fixed, "display_layout", "Displays")
        self.add(fixed)

        # Initialize monitor info
        monitor_name = Gtk.Label()
        monitor_name.set_markup(f"<span font-size='large' font_weight='bold'>{conf['graphics']}</span>")
        fixed.put(monitor_name, 200, 175)

        monitor_res = Gtk.Label()
        monitor_res.set_markup(conf["monitor_res"])
        fixed.put(monitor_res, 275, 225)

        # Initialize monitor image
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(conf["monitor_image_path"], conf["monitor_image_size"][0], conf["monitor_image_size"][1], True)
        monitor_img = Gtk.Image.new_from_pixbuf(pixbuf)
        fixed.put(monitor_img, 230, 50)

    def support_init(self):
        with open(self.overview_json_path, mode="rt") as f:
            conf = json.loads(f.read())

        fixed = Gtk.Fixed()

        # Add the "Support" tab
        self.stack.add_titled(fixed, "support_layout", "Support")
        self.add(fixed)

        # Initialize labels
        support_on_discord = Gtk.Label()
        support_on_discord.set_markup("<span font-size='x-large' font_weight='bold'>Get support on discord</span>")
        fixed.put(support_on_discord, 275, 100)

        support_on_reddit = Gtk.Label()
        support_on_reddit.set_markup("<span font-size='x-large' font_weight='bold'>Get support on reddit</span>")
        fixed.put(support_on_reddit, 275, 200)

        no_warrenty = Gtk.Label()
        no_warrenty.set_markup("<span font_weight='bold'>This Software has no warrenty</span>")
        fixed.put(no_warrenty, 20, 175)

        # Intialize image
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(conf["support_image_path"], conf["support_image_size"][0], conf["support_image_size"][1], True)
        support_img = Gtk.Image.new_from_pixbuf(pixbuf)
        fixed.put(support_img, 75, 90)

        # Initialize buttons
        discord_btn = Gtk.Button(label="Join Discord")
        discord_btn.connect("clicked", self.discord_btn_clicked)
        fixed.put(discord_btn, 500, 97)

        reddit_btn = Gtk.Button(label="Join Reddit")
        reddit_btn.connect("clicked", self.reddit_btn_clicked)
        fixed.put(reddit_btn, 500, 197)

        gitrepo_btn = Gtk.Button(label="Git Repo")
        gitrepo_btn.connect("clicked", self.gitrepo_btn_clicked)
        fixed.put(gitrepo_btn, 35, 300)
    def storage_init(self):
        storage_layout = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        storage_layout.pack_start(Gtk.Label(label="Under development"), True, True, 0)
        self.stack.add_titled(storage_layout, "storage_layout", "Storage")
    def service_init(self):
        service_layout = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        service_layout.pack_start(Gtk.Label(label="Under development"), True, True, 0)
        self.stack.add_titled(service_layout, "service_layout", "Service")

    def discord_btn_clicked(self, widget):
        print("Discord button clicked")
        webbrowser.open("https://discord.gg/naMW5DUFhA")

    def reddit_btn_clicked(self, widget):
        print("Reddit button clicked")
        webbrowser.open("https://www.reddit.com/r/pearos/")

    def gitrepo_btn_clicked(self, widget):
        print("Git Repo button clicked")
        webbrowser.open("https://github.com/RickRollMaster101/About-This-Pearintosh")

clrscr = lambda: os.system("clear")

get_sys_stdout = lambda cmd: subprocess.check_output(cmd, shell=True)

def config_confirm():
    return True

def start_configuration(config_path=DEFAULT_OV_CONF):
    json_data = {
        "distro_image_path": "tux-logo.png",
        "distro_image_size": [160, 160],
        "distro_markup": "",
        "distro_ver": "",
        "hostname": "",
        "cpu": "",
        "memory": "",
        "startup_disk": "",
        "graphics": "",
        "monitor_image_path": "",
        "monitor_image_size": [175, 105],
        "support_image_path": "",
        "support_image_size": [75, 75],
        "monitor_res": "",
        "serial_num": "",
        "overview_margins": [60, 60, 60, 60],
        "section_space": 20,
        "logo_space": 60,
        "system_info_command": "",
        "software_update_command": "",
        "font-family": None
    }

    clrscr()


    # Call neofetch and parse info
    neofetch_output = get_sys_stdout("/usr/bin/neofetch --off --color_blocks=off").decode("utf-8")
    ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    neofetch_output = ansi_escape.sub("", neofetch_output)
    neofetch_output = neofetch_output.replace("\r\n", "\n")
    neofetch_output = neofetch_output.split("\n")
    neofetch_sys_info = {}
    
    for line in neofetch_output:
        line = line.strip().split(":")
        if (len(line) >= 2):
            neofetch_sys_info[line[0].strip()] = ":".join(line[1:None]).strip()

    while True:
        clrscr()
        print("Let's start with your system model.\n")

        print("System model detected.")
        json_data["hostname"] = neofetch_sys_info["Host"]
        print("System model:", json_data["hostname"])

        break

    while True:
        clrscr()
        print("Configuring your distro name and version.\n")
        print("The distro name will be displayed in two parts: the bold part and the non-bold part (better visualized on the github repo or any macOS 'About this Mac' screen)")
        print("For distros that have a codename (e.g. Ubuntu Focal Fossa), the bold part should be 'Ubuntu' and the other should be 'Focal Fossa' (without quotes).")
        

        os_release_output = get_sys_stdout("cat /etc/os-release").decode("utf-8")
        os_release_output = os_release_output.replace('"', '').replace("\r\n", "\n").split("\n")
        os_release = {}
        for line in os_release_output:
            line = line.split("=")
            if (len(line) == 2):
                os_release[line[0].upper()] = line[1].strip()
        
        part1 = os_release["NAME"]
        if "VERSION" in os_release:
            json_data["distro_ver"] = os_release["VERSION"]
        else:
            json_data["distro_ver"] = neofetch_sys_info["Kernel"]

        if "VERSION_CODENAME" in os_release:
            part2 = os_release["VERSION_CODENAME"]
        else:
            part2 = ""

        print("\nDetected information")
        print("Distro name:", part1)
        print("Version codename:", part2)
        print("Distro version:", json_data["distro_ver"])

        json_data["distro_markup"] = f"<span font-size='xx-large'><span font-weight='bold'>{part1}</span> {part2}</span>"
        break
    
    json_data["cpu"] = " ".join([x.strip() for x in reversed(neofetch_sys_info["CPU"].split("@"))])

    clrscr()
    dmid_output = get_sys_stdout("pkexec dmidecode --type memory").decode("utf-8")
    dmid_output = dmid_output.replace("\t", "").replace("\r\n", "\n").split("\n")

    ram_size = 0
    ram_unit = ""
    ram_bus = ""
    ram_technology = ""

    for line in dmid_output:
        line = [x.strip() for x in line.strip().split(":")]

        # Calculate total RAM size in GB first
        if line[0] == "Size":
            s = line[1].split()
            if (s[1] == "GB"):
                ram_size += float(s[0])
            elif (s[1] == "MB"):
                ram_size += float(s[0])/1000
            elif (s[1] == "TB"):
                ram_size += float(s[0])*1000
        
        if ram_size < 1:
            ram_size *= 1000
            ram_unit = "MB"
        elif ram_size > 1000:
            ram_size /= 1000
            ram_unit = "TB"
        else:
            ram_unit = "GB"
        
        # Check RAM bus
        if line[0] == "Speed":
            ram_bus = line[1].replace("MT/s", "MHz")
        
        # Check RAM technology
        if line[0] == "Type":
            ram_technology = line[1]
    
    json_data["memory"] = str(ram_size) + " " + ram_unit + " " + ram_bus + " " + ram_technology


    lsblk_output = get_sys_stdout("lsblk -o mountpoint,name,label --list | grep /").decode("utf-8").replace("\r\n", "\n").split("\n")
    for line in lsblk_output:
        line = line.split()
        if len(line) >= 1 and line[0] == "/":
            if (len(line) >= 3):
                json_data["startup_disk"] = " ".join(line[2:None])
            else:
                json_data["startup_disk"] = line[1]
            break

    #json_data["graphics"] = neofetch_sys_info["GPU"]
    
    gpu_name = subprocess.check_output("curl -s https://raw.githubusercontent.com/RickRollMaster101/About-This-Pearintosh/master/scripts/totally-not-stolen-from-neofetch.sh | bash", shell=True)
    json_data["graphics"] = gpu_name.decode("utf-8").strip("\n") 

    json_data["serial_num"] = get_sys_stdout(r"pkexec dmidecode --type baseboard | grep Serial | sed 's/^[ \t]*Serial Number: //'").decode("utf-8").strip("\n")

    while True:
        clrscr()
        json_data["distro_image_path"] = SCRIPTDIR + "/logo.png"
        break

    # find the display resolution
    output = subprocess.check_output("X=$(xrandr --current | grep '*' | uniq | awk '{print $1}' | cut -d 'x' -f1)" + " && " + "Y=$(xrandr --current | grep '*' | uniq | awk '{print $1}' | cut -d 'x' -f2) && " + "echo $X x $Y", shell=True)
    json_data["monitor_res"] = output.decode("utf-8").strip("\n")    

    json_data["monitor_image_path"] = SCRIPTDIR + "/desktop.png"

    json_data["support_image_path"] = SCRIPTDIR + "/support.png"
    
    with open(config_path, mode="wt") as f:
        json.dump(json_data, f, indent=2)

    clrscr()
    print("Configuration successfully saved to", config_path)

def normal_run(overview_json=DEFAULT_OV_CONF):
    w = MainWindow(overview_json)
    w.connect("destroy", Gtk.main_quit)
    w.show_all()
    Gtk.main()


def print_help():
    print("""
pearOS About - forked by RickRollMaster101 from https://github.com/hungngocphat01/AboutThisMc
Licensed under GPLv3.

RUNNING
    about-this-pear <args>
    about-this-pear: run the program normally. If there is no system info file found, you will be prompted to create one.
    about-this-pear configure: re-execute the configuration procedure.
    about-this-pear configure <path>: execute the configuration procedure and write to a custom path.
    about-this-pear help: show this help message
    about-this-pear load-overview <filename>.json: load a custom overview-info.json file rather than the default one in the installed directory.

""")

def validate_overview_json(path) -> bool:
    if not os.path.exists(path):
        show_error("File not found", f"The specified path doesn not exist: {path}")
        return False
    with open(path, mode="rt") as f:
        json_data = json.loads(f.read())
        
        # Validate keys
        keys = ["distro_image_path", "distro_image_size", "distro_markup", "distro_ver", "hostname", "cpu", "memory", "startup_disk", "graphics", "serial_num", "serial_num", "overview_margins", "section_space", "logo_space", "system_info_command", "software_update_command", "font-family"]
        for key in keys:
            if key not in json_data:
                show_error("Invalid configuration file", f"Missing key: {key}. Please run the configuration procedure again.")
        
        # Evaluate each key
        if not os.path.exists(json_data["distro_image_path"]):
            show_error("Invalid path", f"The specified distro image file cannot be found:\n{json_data['distro_image_path']}")
            return False
        if not isinstance(json_data["distro_image_size"], list):
            show_error("Invalid configuration file", "distro_image_size must be a list.")
            return False
        for item in json_data["distro_image_size"]:
            if not isinstance(item, float) and not isinstance(item, int):
                show_error("Invalid configuration file", "distro_image_size items must be numeric.")
                return False          
        if not isinstance(json_data["overview_margins"], list):
            show_error("Invalid configuration file", "overview_margins must be a list.")
            return False
        for item in json_data["overview_margins"]:
            if not isinstance(item, float) and not isinstance(item, int):
                show_error("Invalid configuration file", "overview_margins items must be numeric.")
                return False     
        return True 

if len(sys.argv) > 1:
    command = sys.argv[1].lower()
else:
    command = None

if command == "configure":
    if len(sys.argv) >= 3:
        start_configuration(sys.argv[2])
    else:
        start_configuration()
elif command == "help":
    print_help()
elif command == "load-overview":
    normal_run(sys.argv[2])
else:
    if not os.path.exists(DEFAULT_OV_CONF):
        start_configuration()
    else:
        normal_run()