import ac
import acsys
import os
import sys
import platform
import configparser
import math

if platform.architecture()[0] == "64bit":
    libdir = 'third_party/lib64'
else:
    libdir = 'third_party/lib'
sys.path.insert(0, os.path.join(os.path.dirname(__file__), libdir))
os.environ['PATH'] = os.environ['PATH'] + ";."

from third_party.sim_info import info

app_path = "apps/python/D Tachometer/"

# Assume config doesn't need to be updated
update_config = False

# Set config file path
config_path = app_path + "config.ini"

# Initialize configparser
config = configparser.ConfigParser()
config.read(config_path)

# Check if config file has appropriate content
if config.has_section("D Tachometer") != True:
    config.add_section("D Tachometer")
    update_config = True


# Load the integer value or set it to default
def get_int(config, key, default):
    global update_config
    try:
        return config.getint("D Tachometer", key)
    except:
        config.set("D Tachometer", key, str(default))
        update_config = True
        return default


# Load the boolean value or set it to default
def get_boolean(config, key, default):
    global update_config
    try:
        return config.getboolean("D Tachometer", key)
    except:
        config.set("D Tachometer", key, str(default))
        update_config = True
        return default


# Load the float value or set it to default
def get_float(config, key, default):
    global update_config
    try:
        return config.getfloat("D Tachometer", key)
    except:
        config.set("D Tachometer", key, str(default))
        update_config = True
        return default


# Load or generate customizable parameters
theme = get_int(config, "theme", 6)
scale = get_float(config, "scale", 100.0) / 100
unit_kmh = get_boolean(config, "unit_kmh", True)
show_drift = get_boolean(config, "show_drift", True)
show_pedal = get_boolean(config, "show_pedal", True)
redLimit_offset = get_int(config, "redLimit_offset", 2000)
fixed_speedo_color = get_boolean(config, "fixed_speedo_color", False)
lower_refresh_rate = get_boolean(config, "lower_refresh_rate", False)

# Update config if necessary
if update_config:
    with open(config_path, 'w') as file_config:
        config.write(file_config)

# Initialize
timer = 0
timer2 = 0
timer3 = 0
status = 0
maxRpm = 0
spin_rate = 1
get_headlights = False
current_car = 0
rpm = 0
gear = 0
speed = 0
gas = 0
brake = 0
angle_fl = 0
angle_fr = 0
angle_rl = 0
angle_rr = 0
alpha = -0.1
speed_list = []

# Window visibilities
settings_window_visibility = 0

# Set image paths
theme_path = "themes/D" + str(theme) + "/"

# Load theme configs
theme_config = app_path + theme_path + "theme_config.ini"
config.read(theme_config)


night_mode_available = config.getboolean("General", "night_mode_available")
pedal_gauge_available = config.getboolean("General", "pedal_gauge_available")
drift_light_available = config.getboolean("General", "drift_light_available")
rev_light_available = config.getboolean("General", "rev_light_available")
variable_speed_color = config.getboolean("General", "variable_speed_color")
has_ae86_gauge = config.getboolean("General", "has_ae86_gauge")


background_width = config.getfloat("Background", "background_width")
background_height = config.getfloat("Background", "background_height")

if pedal_gauge_available:
    background_pedal_width = config.getfloat("Background", "background_pedal_width")
    background_pedal_height = config.getfloat("Background", "background_pedal_height")


gear_x = config.getfloat("Gear", "gear_x")
gear_y = config.getfloat("Gear", "gear_y")
gear_width = config.getfloat("Gear", "gear_width")
gear_height = config.getfloat("Gear", "gear_height")


gauge_x = config.getfloat("RPM Gauge", "gauge_x")
gauge_y = config.getfloat("RPM Gauge", "gauge_y")
gauge_width = config.getfloat("RPM Gauge", "gauge_width")
gauge_height = config.getfloat("RPM Gauge", "gauge_height")
maxRpm_state_0 = config.getfloat("RPM Gauge", "maxRpm_state_0")
maxRpm_state_1 = config.getfloat("RPM Gauge", "maxRpm_state_1")
maxRpm_state_2 = config.getfloat("RPM Gauge", "maxRpm_state_2")
maxRpm_state_3 = config.getfloat("RPM Gauge", "maxRpm_state_3")
maxRpm_state_4 = config.getfloat("RPM Gauge", "maxRpm_state_4")
maxRpm_state_5 = config.getfloat("RPM Gauge", "maxRpm_state_5")
maxRpm_state_6 = config.getfloat("RPM Gauge", "maxRpm_state_6")


degree_available = config.getfloat("RPM Bar", "degree_available")
degree_offset = config.getfloat("RPM Bar", "degree_offset")
rpm_x = config.getfloat("RPM Bar", "rpm_x")
rpm_y = config.getfloat("RPM Bar", "rpm_y")
rpm_width = config.getfloat("RPM Bar", "rpm_width")
rpm_height = config.getfloat("RPM Bar", "rpm_height")
rpm_center_x = config.getfloat("RPM Bar", "rpm_center_x")
rpm_center_y = config.getfloat("RPM Bar", "rpm_center_y")


speed_x = config.getfloat("Speed", "speed_x")
speed_y = config.getfloat("Speed", "speed_y")
speed_width = config.getfloat("Speed", "speed_width")
speed_height = config.getfloat("Speed", "speed_height")
speed_gap = config.getfloat("Speed", "speed_gap")


unit_x = config.getfloat("Speed Unit", "unit_x")
unit_y = config.getfloat("Speed Unit", "unit_y")
unit_width = config.getfloat("Speed Unit", "unit_width")
unit_height = config.getfloat("Speed Unit", "unit_height")


if pedal_gauge_available:
    gas_x = config.getfloat("Pedal", "gas_x")
    gas_y = config.getfloat("Pedal", "gas_y")
    gas_width = config.getfloat("Pedal", "gas_width")
    gas_height = config.getfloat("Pedal", "gas_height")
    brake_x = config.getfloat("Pedal", "brake_x")
    brake_y = config.getfloat("Pedal", "brake_y")
    brake_width = config.getfloat("Pedal", "brake_width")
    brake_height = config.getfloat("Pedal", "brake_height")
    degree_gas = config.getfloat("Pedal", "degree_gas")
    degree_brake = config.getfloat("Pedal", "degree_brake")
    pedal_offset = config.getfloat("Pedal", "pedal_offset")


if drift_light_available:
    drift_x = config.getfloat("Drift Light", "drift_x")
    drift_y = config.getfloat("Drift Light", "drift_y")
    drift_width = config.getfloat("Drift Light", "drift_width")
    drift_height = config.getfloat("Drift Light", "drift_height")


if rev_light_available:
    rev_x = config.getfloat("Rev Light", "rev_x")
    rev_y = config.getfloat("Rev Light", "rev_y")
    rev_width = config.getfloat("Rev Light", "rev_width")
    rev_height = config.getfloat("Rev Light", "rev_height")


# Load Images
preview = app_path + theme_path + "preview.png"


def acMain(ac_version):
    global app_window, settings_window
    global background, background_pedal, drift_background, drift_background_pedal, kmh, mph
    global gear_label, rpm_gauge, night_rpm_gauge, speed_label, speed_unit, speed_digits, speed_red, speed_yellow, speed_blue
    global drift_blue, drift_yellow, rev_light, rpm_bar, night_rpm_bar, gas_label, brake_label
    global theme_label, theme_spinner
    global scale_label, scale_spinner
    global redLimit_offset_label, redLimit_offset_spinner
    global speedo_color_label, speedo_color_checkbox
    global unit_kmh_label, unit_kmh_checkbox
    global show_drift_label, show_drift_checkbox
    global show_pedal_label, show_pedal_checkbox
    global refresh_rate_label, refresh_rate_checkbox
    global preview_label

    # App window
    app_window = ac.newApp("D Tachometer")
    ac.setTitle(app_window, "")
    ac.drawBorder(app_window, 0)
    ac.setIconPosition(app_window, 0, -10000)
    ac.setSize(app_window, background_width * scale, background_height * scale)
    ac.setBackgroundOpacity(app_window, 0)


    background = ac.newTexture(app_path + theme_path + "background/background.png")
    background_pedal = ac.newTexture(app_path + theme_path + "background/background_pedal.png")
    drift_background = ac.newTexture(app_path + theme_path + "background/drift_background.png")
    drift_background_pedal = ac.newTexture(app_path + theme_path + "background/drift_background_pedal.png")
    kmh = ac.newTexture(app_path + theme_path + "speed_unit/kmh.png")
    mph = ac.newTexture(app_path + theme_path + "speed_unit/mph.png")
    gas_label = ac.newTexture(app_path + theme_path + "pedal/gas.png")
    brake_label = ac.newTexture(app_path + theme_path + "pedal/brake.png")

    # Gear
    gear_label = []
    for i in range(11):
        gear_label.append(ac.newTexture(app_path + theme_path + "gears/gear_" + str(i) + ".png"))

    # Speed
    if variable_speed_color:
        speed_red = []
        speed_yellow = []
        speed_blue = []
        for i in range(10):
            speed_red.append(ac.newTexture(app_path + theme_path + "speed_red/speed_digits_" + str(i) + ".png"))
            speed_yellow.append(
                ac.newTexture(app_path + theme_path + "speed_yellow/speed_digits_" + str(i) + ".png"))
            speed_blue.append(ac.newTexture(app_path + theme_path + "speed_blue/speed_digits_" + str(i) + ".png"))
    else:
        speed_digits = []
        for i in range(10):
            speed_digits.append(ac.newTexture(app_path + theme_path + "speed_digits/speed_digits_" + str(i) + ".png"))

    if drift_light_available:
        drift_blue = ac.newTexture(app_path + theme_path + "drift/drift_blue.png")
        drift_yellow = ac.newTexture(app_path + theme_path + "drift/drift_yellow.png")

    if rev_light_available:
        rev_light = ac.newTexture(app_path + theme_path + "rev_light.png")

    if night_mode_available:
        night_rpm_bar = ac.newTexture(app_path + theme_path + "rpm_bar/night_rpm_bar.png")

    rpm_bar = ac.newTexture(app_path + theme_path + "rpm_bar/rpm_bar.png")

    if night_mode_available:
        night_rpm_gauge = []
        for i in ["8k", "9k", "10k", "13k", "16k", "18k", "20k"]:
            night_rpm_gauge.append(ac.newTexture(app_path + theme_path + "background/night_labels_" + i + ".png"))
        if has_ae86_gauge:
            night_rpm_gauge.append(ac.newTexture(app_path + theme_path + "background/night_labels_86.png"))
        #add
        elif theme >= 8:
            night_rpm_gauge.append(ac.newTexture(app_path + theme_path + "background/night_labels_12k.png"))
    rpm_gauge = []
    for i in ["8k", "9k", "10k", "13k", "16k", "18k", "20k"]:
        rpm_gauge.append(ac.newTexture(app_path + theme_path + "background/labels_" + i + ".png"))
    if has_ae86_gauge:
        rpm_gauge.append(ac.newTexture(app_path + theme_path + "background/labels_86.png"))
    elif theme >= 8:
        #add
        rpm_gauge.append(ac.newTexture(app_path + theme_path + "background/labels_12k.png"))
    ac.addRenderCallback(app_window, appGL)


    # Settings window
    settings_window = ac.newApp("Tachometer Settings")
    ac.drawBorder(settings_window, 0)
    ac.setSize(settings_window, 360 * scale, 480 * scale)
    ac.setVisible(settings_window, settings_window_visibility)
    ac.addOnAppActivatedListener(settings_window, settings_window_activated)
    ac.addOnAppDismissedListener(settings_window, settings_window_deactivated)

    # Theme
    theme_label = ac.addLabel(settings_window, "Theme (requires restart)")
    ac.setPosition(theme_label, 10 * scale, 40 * scale)
    ac.setFontSize(theme_label, 20 * scale)
    ac.setVisible(theme_label, 1)

    theme_spinner = ac.addSpinner(settings_window, "")
    #add
    ac.setRange(theme_spinner, 3, 9)
    ac.setStep(theme_spinner, 1)
    ac.setValue(theme_spinner, theme)
    ac.setPosition(theme_spinner, 260 * scale, 40 * scale)
    ac.setSize(theme_spinner, 90 * scale, 25 * scale)
    ac.setFontSize(theme_spinner, 20 * scale)
    ac.addOnValueChangeListener(theme_spinner, theme_spinner_clicked)

    # Scale
    scale_label = ac.addLabel(settings_window, "Scale")
    ac.setPosition(scale_label, 10 * scale, 80 * scale)
    ac.setFontSize(scale_label, 20 * scale)

    scale_spinner = ac.addSpinner(settings_window, "")
    ac.setRange(scale_spinner, 50, 200)
    ac.setStep(scale_spinner, 10)
    ac.setValue(scale_spinner, scale * 100)
    ac.setPosition(scale_spinner, 260 * scale, 80 * scale)
    ac.setSize(scale_spinner, 90 * scale, 25 * scale)
    ac.setFontSize(scale_spinner, 20 * scale)
    ac.addOnValueChangeListener(scale_spinner, scale_spinner_clicked)

    # redLimit_offset
    redLimit_offset_label = ac.addLabel(settings_window, "Shift indicator offset (RPM)")
    ac.setPosition(redLimit_offset_label, 10 * scale, 120 * scale)
    ac.setFontSize(redLimit_offset_label, 20 * scale)

    redLimit_offset_spinner = ac.addSpinner(settings_window, "")
    ac.setRange(redLimit_offset_spinner, 1000, 3000)
    ac.setStep(redLimit_offset_spinner, 500)
    ac.setValue(redLimit_offset_spinner, redLimit_offset)
    ac.setPosition(redLimit_offset_spinner, 260 * scale, 120 * scale)
    ac.setSize(redLimit_offset_spinner, 90 * scale, 25 * scale)
    ac.setFontSize(redLimit_offset_spinner, 20 * scale)
    ac.addOnValueChangeListener(redLimit_offset_spinner, redLimit_offset_spinner_clicked)

    # Drift light
    show_drift_label = ac.addLabel(settings_window, "Show drift light")
    ac.setPosition(show_drift_label, 10 * scale, 160 * scale)
    ac.setFontSize(show_drift_label, 20 * scale)

    show_drift_checkbox = ac.addCheckBox(settings_window, "")
    ac.setValue(show_drift_checkbox, show_drift)
    ac.setPosition(show_drift_checkbox, 330 * scale, 160 * scale)
    ac.setSize(show_drift_checkbox, 20 * scale, 20 * scale)
    ac.addOnCheckBoxChanged(show_drift_checkbox, show_drift_checkbox_clicked)

    # Pedal gauge
    show_pedal_label = ac.addLabel(settings_window, "Show pedal gauge")
    ac.setPosition(show_pedal_label, 10 * scale, 200 * scale)
    ac.setFontSize(show_pedal_label, 20 * scale)

    show_pedal_checkbox = ac.addCheckBox(settings_window, "")
    ac.setValue(show_pedal_checkbox, show_pedal)
    ac.setPosition(show_pedal_checkbox, 330 * scale, 200 * scale)
    ac.setSize(show_pedal_checkbox, 20 * scale, 20 * scale)
    ac.addOnCheckBoxChanged(show_pedal_checkbox, show_pedal_checkbox_clicked)

    # Speed unit
    unit_kmh_label = ac.addLabel(settings_window, "Speed in km/h")
    ac.setPosition(unit_kmh_label, 10 * scale, 240 * scale)
    ac.setFontSize(unit_kmh_label, 20 * scale)

    unit_kmh_checkbox = ac.addCheckBox(settings_window, "")
    ac.setValue(unit_kmh_checkbox, unit_kmh)
    ac.setPosition(unit_kmh_checkbox, 330 * scale, 240 * scale)
    ac.setSize(unit_kmh_checkbox, 20 * scale, 20 * scale)
    ac.addOnCheckBoxChanged(unit_kmh_checkbox, unit_kmh_checkbox_clicked)

    # Fixed speedometer color
    speedo_color_label = ac.addLabel(settings_window, "Fixed speedometer color")
    ac.setPosition(speedo_color_label, 10 * scale, 280 * scale)
    ac.setFontSize(speedo_color_label, 20 * scale)

    speedo_color_checkbox = ac.addCheckBox(settings_window, "")
    ac.setValue(speedo_color_checkbox, fixed_speedo_color)
    ac.setPosition(speedo_color_checkbox, 330 * scale, 280 * scale)
    ac.setSize(speedo_color_checkbox, 20 * scale, 20 * scale)
    ac.addOnCheckBoxChanged(speedo_color_checkbox, speedo_color_checkbox_clicked)

    # Lower refresh rate
    refresh_rate_label = ac.addLabel(settings_window, "Lower refresh rate")
    ac.setPosition(refresh_rate_label, 10 * scale, 320 * scale)
    ac.setFontSize(refresh_rate_label, 20 * scale)

    refresh_rate_checkbox = ac.addCheckBox(settings_window, "")
    ac.setValue(refresh_rate_checkbox, lower_refresh_rate)
    ac.setPosition(refresh_rate_checkbox, 330 * scale, 320 * scale)
    ac.setSize(refresh_rate_checkbox, 20 * scale, 20 * scale)
    ac.addOnCheckBoxChanged(refresh_rate_checkbox, refresh_rate_checkbox_clicked)

    # Preview
    preview_label = ac.addLabel(settings_window, "")
    ac.setPosition(preview_label, 0 * scale, 336 * scale)
    ac.setSize(preview_label, 360 * scale, 144 * scale)
    ac.setBackgroundTexture(preview_label, preview)


def appGL(deltaT):

    ac.glColor4f(1, 1, 1, 1)
    if drift_light_available and show_drift:
        if pedal_gauge_available and show_pedal:
            ac.glQuadTextured(0, 0, background_pedal_width * scale, background_pedal_height * scale, drift_background_pedal)
        else:
            ac.glQuadTextured(0, 0, background_width * scale, background_height * scale, drift_background)
    else:
        if pedal_gauge_available and show_pedal:
            ac.glQuadTextured(0, 0, background_pedal_width * scale, background_pedal_height * scale, background_pedal)
        else:
            ac.glQuadTextured(0, 0, background_width * scale, background_height * scale, background)

    if unit_kmh:
        ac.glQuadTextured(unit_x * scale, unit_y * scale, unit_width * scale, unit_height * scale, kmh)
    else:
        ac.glQuadTextured(unit_x * scale, unit_y * scale, unit_width * scale, unit_height * scale, mph)


    ac.glColor4f(1, 1, 1, 1)
    ac.glBegin(acsys.GL.Quads)

    #add
    if theme >= 8:
        spin_rate = (12000 / degree_available)
        if night_mode_available and get_headlights:
            ac.ext_glSetTexture(night_rpm_gauge[7])
        else:
            ac.ext_glSetTexture(rpm_gauge[7])
    else:
        if has_ae86_gauge and car_name.find("ae86") > 0 and maxRpm < 8500:
            spin_rate = (8000 / degree_available)
            if night_mode_available and get_headlights:
                ac.ext_glSetTexture(night_rpm_gauge[7])
            else:
                ac.ext_glSetTexture(rpm_gauge[7])
        else:
            if maxRpm > maxRpm_state_6:
                spin_rate = (20000 / degree_available)
                if night_mode_available and get_headlights:
                    ac.ext_glSetTexture(night_rpm_gauge[6])
                else:
                    ac.ext_glSetTexture(rpm_gauge[6])
            elif maxRpm > maxRpm_state_5:
                spin_rate = (18000 / degree_available)
                if night_mode_available and get_headlights:
                    ac.ext_glSetTexture(night_rpm_gauge[5])
                else:
                    ac.ext_glSetTexture(rpm_gauge[5])
            elif maxRpm > maxRpm_state_4:
                spin_rate = (16000 / degree_available)
                if night_mode_available and get_headlights:
                    ac.ext_glSetTexture(night_rpm_gauge[4])
                else:
                    ac.ext_glSetTexture(rpm_gauge[4])
            elif maxRpm > maxRpm_state_3:
                spin_rate = (13000 / degree_available)
                if night_mode_available and get_headlights:
                    ac.ext_glSetTexture(night_rpm_gauge[3])
                else:
                    ac.ext_glSetTexture(rpm_gauge[3])
            elif maxRpm > maxRpm_state_2:
                spin_rate = (10000 / degree_available)
                if night_mode_available and get_headlights:
                    ac.ext_glSetTexture(night_rpm_gauge[2])
                else:
                    ac.ext_glSetTexture(rpm_gauge[2])
            elif maxRpm > maxRpm_state_1:
                spin_rate = (9000 / degree_available)
                if night_mode_available and get_headlights:
                    ac.ext_glSetTexture(night_rpm_gauge[1])
                else:
                    ac.ext_glSetTexture(rpm_gauge[1])
            elif maxRpm > maxRpm_state_0:
                spin_rate = (8000 / degree_available)
                if night_mode_available and get_headlights:
                    ac.ext_glSetTexture(night_rpm_gauge[0])
                else:
                    ac.ext_glSetTexture(rpm_gauge[0])
            else:
                spin_rate = (10000 / degree_available)
                if night_mode_available and get_headlights:
                    ac.ext_glSetTexture(night_rpm_gauge[2])
                else:
                    ac.ext_glSetTexture(rpm_gauge[2])

    ac.ext_glVertexTex(gauge_x * scale, gauge_y * scale, 0, 0)
    ac.ext_glVertexTex(gauge_x * scale, (gauge_y + gauge_height) * scale, 0, 1)
    ac.ext_glVertexTex((gauge_x + gauge_width) * scale, (gauge_y + gauge_height) * scale, 1, 1)
    ac.ext_glVertexTex((gauge_x + gauge_width) * scale, gauge_y * scale, 1, 0)

    ac.glEnd()


    ac.glColor4f(1, 1, 1, 1)
    ac.glBegin(acsys.GL.Quads)

    if night_mode_available and get_headlights:
        ac.ext_glSetTexture(night_rpm_bar)
    else:
        ac.ext_glSetTexture(rpm_bar)
    ac.ext_glTexCoord2f(0, 0)
    ac.glVertex2f((rpm_center_x + (rpm_x - rpm_center_x) * math.cos(math.radians(rpm / spin_rate + degree_offset)) - (rpm_y - rpm_center_y) * math.sin(math.radians(rpm / spin_rate + degree_offset))) * scale,
                  (rpm_center_y + (rpm_x - rpm_center_x) * math.sin(math.radians(rpm / spin_rate + degree_offset)) + (rpm_y - rpm_center_y) * math.cos(math.radians(rpm / spin_rate + degree_offset))) * scale)

    ac.ext_glTexCoord2f(0, 1)
    ac.glVertex2f((rpm_center_x + (rpm_x - rpm_center_x) * math.cos(math.radians(rpm / spin_rate + degree_offset)) - (rpm_y + rpm_height - rpm_center_y) * math.sin(math.radians(rpm / spin_rate + degree_offset))) * scale,
                  (rpm_center_y + (rpm_x - rpm_center_x) * math.sin(math.radians(rpm / spin_rate + degree_offset)) + (rpm_y + rpm_height - rpm_center_y) * math.cos(math.radians(rpm / spin_rate + degree_offset))) * scale)

    ac.ext_glTexCoord2f(1, 1)
    ac.glVertex2f((rpm_center_x + (rpm_x + rpm_width - rpm_center_x) * math.cos(math.radians(rpm / spin_rate + degree_offset)) - (rpm_y + rpm_height - rpm_center_y) * math.sin(math.radians(rpm / spin_rate + degree_offset))) * scale,
                  (rpm_center_y + (rpm_x + rpm_width - rpm_center_x) * math.sin(math.radians(rpm / spin_rate + degree_offset)) + (rpm_y + rpm_height - rpm_center_y) * math.cos(math.radians(rpm / spin_rate + degree_offset))) * scale)

    ac.ext_glTexCoord2f(1, 0)
    ac.glVertex2f((rpm_center_x + (rpm_x + rpm_width - rpm_center_x) * math.cos(math.radians(rpm / spin_rate + degree_offset)) - (rpm_y - rpm_center_y) * math.sin(math.radians(rpm / spin_rate + degree_offset))) * scale,
                  (rpm_center_y + (rpm_x + rpm_width - rpm_center_x) * math.sin(math.radians(rpm / spin_rate + degree_offset)) + (rpm_y - rpm_center_y) * math.cos(math.radians(rpm / spin_rate + degree_offset))) * scale)

    ac.glEnd()

    if pedal_gauge_available and show_pedal:
        degreeGas = gas * degree_gas
        degreeBrake = brake * degree_brake
        pedal_center_x = gas_x
        pedal_center_y = gas_y + (gas_height / 2)

        if degreeGas < 45:
            coord_1 = math.tan(math.radians(degreeGas))
        else:
            coord_1 = 1

        ac.glColor4f(1, 1, 1, 1)
        ac.glBegin(acsys.GL.Triangles)
        ac.ext_glSetTexture(gas_label)

        ac.ext_glTexCoord2f(0, 0)
        # ac.glVertex2f(gas_x, gas_y)
        ac.glVertex2f((pedal_center_x + (gas_x - pedal_center_x) * math.cos(
            math.radians(pedal_offset)) - (gas_y - pedal_center_y) * math.sin(
            math.radians(pedal_offset))) * scale,
                      (pedal_center_y + (gas_x - pedal_center_x) * math.sin(
                          math.radians(pedal_offset)) + (gas_y - pedal_center_y) * math.cos(
                          math.radians(pedal_offset))) * scale)

        ac.ext_glTexCoord2f(0, 0.5)
        ac.glVertex2f(pedal_center_x * scale, pedal_center_y * scale)

        ac.ext_glTexCoord2f(coord_1, 0)
        # ac.glVertex2f(gas_x + (gas_width * coord_1), gas_y)
        ac.glVertex2f((pedal_center_x + (gas_x + (gas_width * coord_1) - pedal_center_x) * math.cos(
            math.radians(pedal_offset)) - (gas_y - pedal_center_y) * math.sin(
            math.radians(pedal_offset))) * scale,
                      (pedal_center_y + (gas_x + (gas_width * coord_1) - pedal_center_x) * math.sin(
                          math.radians(pedal_offset)) + (gas_y - pedal_center_y) * math.cos(
                          math.radians(pedal_offset))) * scale)

        ac.glEnd()

        if degreeGas > 45:
            if degreeGas > 90:
                coord_2 = 0.5
            else:
                coord_2 = (1 - (math.tan(math.radians(90 - degreeGas)))) / 2
            ac.glColor4f(1, 1, 1, 1)
            ac.glBegin(acsys.GL.Triangles)
            ac.ext_glSetTexture(gas_label)

            ac.ext_glTexCoord2f(1, 0)
            # ac.glVertex2f(gas_x + gas_width, gas_y)
            ac.glVertex2f((pedal_center_x + (gas_x + gas_width - pedal_center_x) * math.cos(
                math.radians(pedal_offset)) - (gas_y - pedal_center_y) * math.sin(
                math.radians(pedal_offset))) * scale,
                          (pedal_center_y + (gas_x + gas_width - pedal_center_x) * math.sin(
                              math.radians(pedal_offset)) + (gas_y - pedal_center_y) * math.cos(
                              math.radians(pedal_offset))) * scale)

            ac.ext_glTexCoord2f(0, 0.5)
            ac.glVertex2f(pedal_center_x * scale, pedal_center_y * scale)

            ac.ext_glTexCoord2f(1, coord_2)
            # ac.glVertex2f(gas_x + gas_width, gas_y + (gas_height * coord_2))
            ac.glVertex2f((pedal_center_x + (gas_x + gas_width - pedal_center_x) * math.cos(
                math.radians(pedal_offset)) - (gas_y + (gas_height * coord_2) - pedal_center_y) * math.sin(
                math.radians(pedal_offset))) * scale,
                          (pedal_center_y + (gas_x + gas_width - pedal_center_x) * math.sin(
                              math.radians(pedal_offset)) + (gas_y + (gas_height * coord_2) - pedal_center_y) * math.cos(
                              math.radians(pedal_offset))) * scale)

            ac.glEnd()

        if degreeGas > 90:
            if degreeGas > 135:
                coord_3 = 1
            else:
                coord_3 = 0.5 + (math.tan(math.radians(degreeGas - 90)) / 2)
            ac.glColor4f(1, 1, 1, 1)
            ac.glBegin(acsys.GL.Triangles)
            ac.ext_glSetTexture(gas_label)

            ac.ext_glTexCoord2f(1, 0.5)
            # ac.glVertex2f(gas_x + gas_width, gas_y + (gas_height / 2))
            ac.glVertex2f((pedal_center_x + (gas_x + gas_width - pedal_center_x) * math.cos(
                math.radians(pedal_offset)) - (pedal_center_y - pedal_center_y) * math.sin(
                math.radians(pedal_offset))) * scale,
                          (pedal_center_y + (gas_x + gas_width - pedal_center_x) * math.sin(
                              math.radians(pedal_offset)) + (pedal_center_y - pedal_center_y) * math.cos(
                              math.radians(pedal_offset))) * scale)

            ac.ext_glTexCoord2f(0, 0.5)
            ac.glVertex2f(pedal_center_x * scale, pedal_center_y * scale)

            ac.ext_glTexCoord2f(1, coord_3)
            # ac.glVertex2f(gas_x + gas_width, gas_y + (gas_height * coord_3))
            ac.glVertex2f((pedal_center_x + (gas_x + gas_width - pedal_center_x) * math.cos(
                math.radians(pedal_offset)) - (gas_y + (gas_height * coord_3) - pedal_center_y) * math.sin(
                math.radians(pedal_offset))) * scale,
                          (pedal_center_y + (gas_x + gas_width - pedal_center_x) * math.sin(
                              math.radians(pedal_offset)) + (gas_y + (gas_height * coord_3) - pedal_center_y) * math.cos(
                              math.radians(pedal_offset))) * scale)

            ac.glEnd()

        if degreeBrake < 45:
            coord_1 = math.tan(math.radians(degreeBrake))
        else:
            coord_1 = 1

        ac.glColor4f(1, 1, 1, 1)
        ac.glBegin(acsys.GL.Triangles)
        ac.ext_glSetTexture(brake_label)

        ac.ext_glTexCoord2f(0, 0)
        # ac.glVertex2f(brake_x, brake_y)
        ac.glVertex2f((pedal_center_x + (brake_x - pedal_center_x) * math.cos(
            math.radians(pedal_offset)) - (brake_y - pedal_center_y) * math.sin(
            math.radians(pedal_offset))) * scale,
                      (pedal_center_y + (brake_x - pedal_center_x) * math.sin(
                          math.radians(pedal_offset)) + (brake_y - pedal_center_y) * math.cos(
                          math.radians(pedal_offset))) * scale)

        ac.ext_glTexCoord2f(0, 0.5)
        ac.glVertex2f(pedal_center_x * scale, pedal_center_y * scale)

        ac.ext_glTexCoord2f(coord_1, 0)
        # ac.glVertex2f(brake_x + (brake_width * coord_1), brake_y)
        ac.glVertex2f((pedal_center_x + (brake_x + (brake_width * coord_1) - pedal_center_x) * math.cos(
            math.radians(pedal_offset)) - (brake_y - pedal_center_y) * math.sin(
            math.radians(pedal_offset))) * scale,
                      (pedal_center_y + (brake_x + (brake_width * coord_1) - pedal_center_x) * math.sin(
                          math.radians(pedal_offset)) + (brake_y - pedal_center_y) * math.cos(
                          math.radians(pedal_offset))) * scale)

        ac.glEnd()

        if degreeBrake > 45:
            if degreeBrake > 90:
                coord_2 = 0.5
            else:
                coord_2 = (1 - (math.tan(math.radians(90 - degreeBrake)))) / 2
            ac.glColor4f(1, 1, 1, 1)
            ac.glBegin(acsys.GL.Triangles)
            ac.ext_glSetTexture(brake_label)

            ac.ext_glTexCoord2f(1, 0)
            # ac.glVertex2f(brake_x + brake_width, brake_y)
            ac.glVertex2f((pedal_center_x + (brake_x + brake_width - pedal_center_x) * math.cos(
                math.radians(pedal_offset)) - (brake_y - pedal_center_y) * math.sin(
                math.radians(pedal_offset))) * scale,
                          (pedal_center_y + (brake_x + brake_width - pedal_center_x) * math.sin(
                              math.radians(pedal_offset)) + (brake_y - pedal_center_y) * math.cos(
                              math.radians(pedal_offset))) * scale)

            ac.ext_glTexCoord2f(0, 0.5)
            ac.glVertex2f(pedal_center_x * scale, pedal_center_y * scale)

            ac.ext_glTexCoord2f(1, coord_2)
            # ac.glVertex2f(brake_x + brake_width, brake_y + (brake_height * coord_2))
            ac.glVertex2f((pedal_center_x + (brake_x + brake_width - pedal_center_x) * math.cos(
                math.radians(pedal_offset)) - (brake_y + (brake_height * coord_2) - pedal_center_y) * math.sin(
                math.radians(pedal_offset))) * scale,
                          (pedal_center_y + (brake_x + brake_width - pedal_center_x) * math.sin(
                              math.radians(pedal_offset)) + (brake_y + (brake_height * coord_2) - pedal_center_y) * math.cos(
                              math.radians(pedal_offset))) * scale)

            ac.glEnd()

        if degreeBrake > 90:
            if degreeBrake > 135:
                coord_3 = 1
            else:
                coord_3 = 0.5 + (math.tan(math.radians(degreeBrake - 90)) / 2)
            ac.glColor4f(1, 1, 1, 1)
            ac.glBegin(acsys.GL.Triangles)
            ac.ext_glSetTexture(brake_label)

            ac.ext_glTexCoord2f(1, 0.5)
            # ac.glVertex2f(brake_x + brake_width, brake_y + (brake_height / 2))
            ac.glVertex2f((pedal_center_x + (brake_x + brake_width - pedal_center_x) * math.cos(
                math.radians(pedal_offset)) - (pedal_center_y - pedal_center_y) * math.sin(
                math.radians(pedal_offset))) * scale,
                          (pedal_center_y + (brake_x + brake_width - pedal_center_x) * math.sin(
                              math.radians(pedal_offset)) + (pedal_center_y - pedal_center_y) * math.cos(
                              math.radians(pedal_offset))) * scale)

            ac.ext_glTexCoord2f(0, 0.5)
            ac.glVertex2f(pedal_center_x * scale, pedal_center_y * scale)

            ac.ext_glTexCoord2f(1, coord_3)
            # ac.glVertex2f(brake_x + brake_width, brake_y + (brake_height * coord_3))
            ac.glVertex2f((pedal_center_x + (brake_x + brake_width - pedal_center_x) * math.cos(
                math.radians(pedal_offset)) - (brake_y + (brake_height * coord_3) - pedal_center_y) * math.sin(
                math.radians(pedal_offset))) * scale,
                          (pedal_center_y + (brake_x + brake_width - pedal_center_x) * math.sin(
                              math.radians(pedal_offset)) + (brake_y + (brake_height * coord_3) - pedal_center_y) * math.cos(
                              math.radians(pedal_offset))) * scale)

            ac.glEnd()

    if status != 1 and drift_light_available and show_drift:
        if angle_car > 30 and speed > 5:
            ac.glColor4f(1, 1, 1, 1)
            ac.glQuadTextured(drift_x * scale, drift_y * scale, drift_width * scale, drift_height * scale,
                              drift_yellow)
        elif angle_car > 15 and speed > 5:
            ac.glColor4f(1, 1, 1, alpha)
            ac.glQuadTextured(drift_x * scale, drift_y * scale, drift_width * scale, drift_height * scale,
                              drift_blue)

    if rev_light_available:
        if maxRpm - rpm < 250:
            ac.glColor4f(1, 1, 1, 1)
            ac.glQuadTextured(rev_x * scale, rev_y * scale, rev_width * scale, rev_height * scale, rev_light)
        elif maxRpm - rpm < redLimit_offset:
            ac.glColor4f(1, 1, 1, ((rpm - maxRpm) / redLimit_offset) + 1)
            ac.glQuadTextured(rev_x * scale, rev_y * scale, rev_width * scale, rev_height * scale, rev_light)


    if variable_speed_color:
        if fixed_speedo_color:
            ac.glColor4f(1, 1, 1, 1)
            for i in range(len(speed_list)):
                ac.glQuadTextured((speed_x - i * (speed_width + speed_gap)) * scale, speed_y * scale,
                                    speed_width * scale, speed_height * scale, speed_blue[int((speed_list[::-1])[i])])
        else:
            if speed < 100:
                ac.glColor4f(1, 1, 1, 1)
                for i in range(len(speed_list)):
                    ac.glQuadTextured((speed_x - i * (speed_width + speed_gap)) * scale, speed_y * scale,
                                        speed_width * scale, speed_height * scale,
                                        speed_red[int((speed_list[::-1])[i])])
            elif speed < 150:
                ac.glColor4f(1, 1, 1, 1)
                for i in range(len(speed_list)):
                    ac.glQuadTextured((speed_x - i * (speed_width + speed_gap)) * scale, speed_y * scale,
                                        speed_width * scale, speed_height * scale,
                                        speed_yellow[int((speed_list[::-1])[i])])
            else:
                ac.glColor4f(1, 1, 1, 1)
                for i in range(len(speed_list)):
                    ac.glQuadTextured((speed_x - i * (speed_width + speed_gap)) * scale, speed_y * scale,
                                        speed_width * scale, speed_height * scale,
                                        speed_blue[int((speed_list[::-1])[i])])
    else:
        ac.glColor4f(1, 1, 1, 1)
        for i in range(len(speed_list)):
            ac.glQuadTextured((speed_x - i * (speed_width + speed_gap)) * scale, speed_y * scale,
                                speed_width * scale,
                                speed_height * scale, speed_digits[int((speed_list[::-1])[i])])

    ac.glColor4f(1, 1, 1, 1)
    ac.glQuadTextured(gear_x * scale, gear_y * scale, gear_width * scale, gear_height * scale, gear_label[gear])


# Settings window
def settings_window_activated(*args):
    global settings_window_visibility

    settings_window_visibility = 1


def settings_window_deactivated(*args):
    global settings_window_visibility

    settings_window_visibility = 0


# Settings window listeners
def scale_spinner_clicked(*args):
    global config, update_config, scale

    update_config = True
    scale = ac.getValue(scale_spinner) / 100

    config.set("D Tachometer", "scale", str(ac.getValue(scale_spinner)))


def unit_kmh_checkbox_clicked(*args):
    global config, update_config, unit_kmh

    update_config = True

    if unit_kmh:
        unit_kmh = False
    else:
        unit_kmh = True

    config.set("D Tachometer", "unit_kmh", str(unit_kmh))


def refresh_rate_checkbox_clicked(*args):
    global config, update_config, lower_refresh_rate

    update_config = True

    if lower_refresh_rate:
        lower_refresh_rate = False
    else:
        lower_refresh_rate = True

    config.set("D Tachometer", "lower_refresh_rate", str(lower_refresh_rate))


def theme_spinner_clicked(*args):
    global config, update_config, preview_label

    update_config = True
    ac.setBackgroundTexture(preview_label,
                            app_path + "themes/D" + "{:.0f}".format(ac.getValue(theme_spinner)) + "/preview.png")

    config.set("D Tachometer", "theme", "{:.0f}".format(ac.getValue(theme_spinner)))


def redLimit_offset_spinner_clicked(*args):
    global config, update_config, redLimit_offset

    update_config = True

    redLimit_offset = ac.getValue(redLimit_offset_spinner)

    config.set("D Tachometer", "redLimit_offset", "{:.0f}".format(ac.getValue(redLimit_offset_spinner)))


def speedo_color_checkbox_clicked(*args):
    global config, update_config, fixed_speedo_color

    update_config = True

    if fixed_speedo_color:
        fixed_speedo_color = False
    else:
        fixed_speedo_color = True

    config.set("D Tachometer", "fixed_speedo_color", str(fixed_speedo_color))


def show_drift_checkbox_clicked(*args):
    global config, update_config, show_drift

    update_config = True

    if show_drift:
        show_drift = False
    else:
        show_drift = True

    config.set("D Tachometer", "show_drift", str(show_drift))


def show_pedal_checkbox_clicked(*args):
    global config, update_config, show_pedal

    update_config = True

    if show_pedal:
        show_pedal = False
    else:
        show_pedal = True

    config.set("D Tachometer", "show_pedal", str(show_pedal))


def acUpdate(deltaT):
    global timer, timer2, timer3
    global status, current_car, maxRpm
    global rpm, speed, gear, gas, brake
    global flash_rate, alpha
    global angle_fl, angle_fr, angle_rl, angle_rr, angle_car
    global get_headlights
    global car_name
    global speed_list

    if alpha < 0:
        flash_rate = 7.2
    elif alpha > 1.2:
        flash_rate = -7.2

    if status != 1 and drift_light_available and show_drift:
        alpha += (deltaT * flash_rate)

    # Update the timers
    timer += deltaT
    timer2 += deltaT
    if lower_refresh_rate:
        timer3 += deltaT

    # Calculate data 1 times per second
    if timer > 1:
        timer = 0

        maxRpm = info.static.maxRpm
        status = info.graphics.status

        ac.setBackgroundOpacity(app_window, 0)

    # Calculate data 10 times per second
    if timer2 > 0.1:
        timer2 = 0

        current_car = ac.getFocusedCar()
        get_headlights = ac.ext_getHeadlights(current_car)

        if has_ae86_gauge:
            car_name = ac.getCarName(current_car)

        if status != 1 and drift_light_available and show_drift:
            angle_fl, angle_fr, angle_rl, angle_rr = ac.getCarState(current_car, acsys.CS.SlipAngle)
            angle_car = abs((angle_rl + angle_rr) / 2)

        gear = ac.getCarState(current_car, acsys.CS.Gear)

        if lower_refresh_rate:
            if unit_kmh:
                speed = ac.getCarState(current_car, acsys.CS.SpeedKMH)
            else:
                speed = ac.getCarState(current_car, acsys.CS.SpeedMPH)

            speed_list = list("{:.0f}".format(speed))

    # Calculate data 30 times per second
    if lower_refresh_rate:
        if timer3 > 0.0333:
            timer3 = 0

            rpm = ac.getCarState(current_car, acsys.CS.RPM)
            if pedal_gauge_available and show_pedal:
                gas = ac.getCarState(current_car, acsys.CS.Gas)
                gas = ac.getCarState(current_car, acsys.CS.Gas)
                brake = ac.getCarState(current_car, acsys.CS.Brake)

    # Calculate data as fast as FPS
    else:
        rpm = ac.getCarState(current_car, acsys.CS.RPM)

        if unit_kmh:
            speed = ac.getCarState(current_car, acsys.CS.SpeedKMH)
        else:
            speed = ac.getCarState(current_car, acsys.CS.SpeedMPH)

        speed_list = list("{:.0f}".format(speed))

        if pedal_gauge_available and show_pedal:
            gas = ac.getCarState(current_car, acsys.CS.Gas)
            brake = ac.getCarState(current_car, acsys.CS.Brake)


def acShutdown():
    global config, update_config, config_path

    # Update config if needed
    if update_config:
        with open(config_path, 'w') as file_config:
            config.write(file_config)
