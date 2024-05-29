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

app_path = "apps/python/D Turbo/"

# Assume config doesn't need to be updated
update_config = False

# Set config file path
config_path = app_path + "config.ini"

# Initialize configparser
config = configparser.ConfigParser()
config.read(config_path)

# Check if config file has appropriate content
if config.has_section("D Turbo") != True:
    config.add_section("D Turbo")
    update_config = True


# Load the boolean value or set it to default
def get_boolean(config, key, default):
    global update_config
    try:
        return config.getboolean("D Turbo", key)
    except:
        config.set("D Turbo", key, str(default))
        update_config = True
        return default


# Load the float value or set it to default
def get_float(config, key, default):
    global update_config
    try:
        return config.getfloat("D Turbo", key)
    except:
        config.set("D Turbo", key, str(default))
        update_config = True
        return default


# Load the integer value or set it to default
def get_int(config, key, default):
    global update_config
    try:
        return config.getint("D Turbo", key)
    except:
        config.set("D Turbo", key, str(default))
        update_config = True
        return default


# Load or generate customizable parameters
theme = get_int(config, "theme", 6)
scale = get_float(config, "scale", 100.0) / 100
unit_bar = get_boolean(config, "unit_bar", True)
lower_refresh_rate = get_boolean(config, "lower_refresh_rate", False)
turbo_amount = get_int(config, "turbo_amount", 1)

# Update config if necessary
if update_config:
    with open(config_path, 'w') as file_config:
        config.write(file_config)

# Timers
timer = 0
timer2 = 0
current_car = 0
boost = 0
get_headlights = 0

# Window visibilities
settings_window_visibility = 0

# Set image paths
theme_path = "themes/D" + str(theme) + "/"

theme_config = app_path + theme_path + "theme_config.ini"
config.read(theme_config)

night_mode_available = config.getboolean("General", "night_mode_available")

background_width = config.getfloat("Background", "background_width")
background_height = config.getfloat("Background", "background_height")

gauge_x = config.getfloat("Boost Gauge", "gauge_x")
gauge_y = config.getfloat("Boost Gauge", "gauge_y")
gauge_width = config.getfloat("Boost Gauge", "gauge_width")
gauge_height = config.getfloat("Boost Gauge", "gauge_height")

degree_available = config.getfloat("Boost Bar", "degree_available")
degree_offset = config.getfloat("Boost Bar", "degree_offset")
boost_x = config.getfloat("Boost Bar", "boost_x")
boost_y = config.getfloat("Boost Bar", "boost_y")
boost_width = config.getfloat("Boost Bar", "boost_width")
boost_height = config.getfloat("Boost Bar", "boost_height")
boost_center_x = config.getfloat("Boost Bar", "boost_center_x")
boost_center_y = config.getfloat("Boost Bar", "boost_center_y")

background = app_path + theme_path + "background/background.png"
preview = app_path + theme_path + "preview.png"

def acMain(ac_version):
    global app_window, settings_window
    global boost_gauge, spin_rate
    global background
    global boost_bar, labels_bar, labels_psi
    global night_boost_bar, night_labels_bar, night_labels_psi
    global theme_label, theme_spinner
    global turbo_amount_label, turbo_amount_spinner
    global scale_label, scale_spinner
    global unit_bar_label, unit_bar_checkbox
    global refresh_rate_label, refresh_rate_checkbox
    global preview_label

    if unit_bar:
        spin_rate = degree_available / 3
    else:
        spin_rate = degree_available / 4.5

    # App window
    app_window = ac.newApp("D Turbo")
    ac.setTitle(app_window, "")
    ac.drawBorder(app_window, 0)
    ac.setIconPosition(app_window, 0, -10000)
    ac.setSize(app_window, background_width * scale, background_height * scale)
    ac.setBackgroundOpacity(app_window, 0)

    # Small hack to prevent render bug
    boost_gauge = ac.addLabel(app_window, "-")
    ac.setPosition(boost_gauge, 0 * scale, -10000 * scale)

    background = ac.newTexture(app_path + theme_path + "background/background.png")
    boost_bar = ac.newTexture(app_path + theme_path + "boost_bar/boost_bar.png")
    labels_bar = ac.newTexture(app_path + theme_path + "background/labels_bar.png")
    labels_psi = ac.newTexture(app_path + theme_path + "background/labels_psi.png")

    if night_mode_available:
        night_boost_bar = ac.newTexture(app_path + theme_path + "boost_bar/night_boost_bar.png")
        night_labels_bar = ac.newTexture(app_path + theme_path + "background/night_labels_bar.png")
        night_labels_psi = ac.newTexture(app_path + theme_path + "background/night_labels_psi.png")

    ac.addRenderCallback(app_window, appGL)

    # Settings window
    settings_window = ac.newApp("Turbo Settings")
    ac.drawBorder(settings_window, 0)
    ac.setSize(settings_window, 360 * scale, 420 * scale)
    ac.setVisible(settings_window, settings_window_visibility)
    ac.addOnAppActivatedListener(settings_window, settings_window_activated)
    ac.addOnAppDismissedListener(settings_window, settings_window_deactivated)

    # Theme
    theme_label = ac.addLabel(settings_window, "Theme (requires restart)")
    ac.setPosition(theme_label, 10 * scale, 40 * scale)
    ac.setFontSize(theme_label, 20 * scale)

    theme_spinner = ac.addSpinner(settings_window, "")
    #add 3, 7
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

    # Boost unit
    unit_bar_label = ac.addLabel(settings_window, "Boost unit in bar")
    ac.setPosition(unit_bar_label, 10 * scale, 120 * scale)
    ac.setFontSize(unit_bar_label, 20 * scale)

    unit_bar_checkbox = ac.addCheckBox(settings_window, "")
    ac.setValue(unit_bar_checkbox, unit_bar)
    ac.setPosition(unit_bar_checkbox, 330 * scale, 120 * scale)
    ac.setSize(unit_bar_checkbox, 20 * scale, 20 * scale)
    ac.addOnCheckBoxChanged(unit_bar_checkbox, unit_bar_checkbox_clicked)

    # Lower refresh rate
    refresh_rate_label = ac.addLabel(settings_window, "Lower refresh rate")
    ac.setPosition(refresh_rate_label, 10 * scale, 160 * scale)
    ac.setFontSize(refresh_rate_label, 20 * scale)

    refresh_rate_checkbox = ac.addCheckBox(settings_window, "")
    ac.setValue(refresh_rate_checkbox, lower_refresh_rate)
    ac.setPosition(refresh_rate_checkbox, 330 * scale, 160 * scale)
    ac.setSize(refresh_rate_checkbox, 20 * scale, 20 * scale)
    ac.addOnCheckBoxChanged(refresh_rate_checkbox, refresh_rate_checkbox_clicked)

    # Patch for multi turbos
    turbo_amount_label = ac.addLabel(settings_window, "Patch for multi turbos")
    ac.setPosition(turbo_amount_label, 10 * scale, 200 * scale)
    ac.setFontSize(turbo_amount_label, 20 * scale)

    turbo_amount_spinner = ac.addSpinner(settings_window, "")
    ac.setRange(turbo_amount_spinner, 1, 4)
    ac.setStep(turbo_amount_spinner, 1)
    ac.setValue(turbo_amount_spinner, turbo_amount)
    ac.setPosition(turbo_amount_spinner, 260 * scale, 200 * scale)
    ac.setSize(turbo_amount_spinner, 90 * scale, 25 * scale)
    ac.setFontSize(turbo_amount_spinner, 20 * scale)
    ac.addOnValueChangeListener(turbo_amount_spinner, turbo_amount_spinner_clicked)

    # Preview
    preview_label = ac.addLabel(settings_window, "")
    ac.setPosition(preview_label, 0 * scale, 236 * scale)
    ac.setSize(preview_label, 360 * scale, 144 * scale)
    ac.setBackgroundTexture(preview_label, preview)


def appGL(deltaT):
    ac.glColor4f(1, 1, 1, 1)
    ac.glQuadTextured(0, 0, background_width * scale, background_height * scale, background)

    ac.glColor4f(1, 1, 1, 1)
    ac.glBegin(acsys.GL.Quads)

    if night_mode_available and get_headlights:
        if unit_bar:
            ac.ext_glSetTexture(night_labels_bar)
        else:
            ac.ext_glSetTexture(night_labels_psi)
    else:
        if unit_bar:
            ac.ext_glSetTexture(labels_bar)
        else:
            ac.ext_glSetTexture(labels_psi)

    ac.ext_glVertexTex(gauge_x * scale, gauge_y * scale, 0, 0)
    ac.ext_glVertexTex((gauge_x + gauge_width) * scale, gauge_y * scale, 1, 0)
    ac.ext_glVertexTex((gauge_x + gauge_width) * scale, (gauge_y + gauge_height) * scale, 1, 1)
    ac.ext_glVertexTex(gauge_x * scale, (gauge_y + gauge_height) * scale, 0, 1)

    ac.glEnd()


    ac.glColor4f(1, 1, 1, 1)
    ac.glBegin(acsys.GL.Quads)

    if night_mode_available and get_headlights:
        ac.ext_glSetTexture(night_boost_bar)
    else:
        ac.ext_glSetTexture(boost_bar)

    ac.ext_glTexCoord2f(0, 0)
    ac.glVertex2f((boost_center_x + (boost_x - boost_center_x) * math.cos(math.radians(boost * spin_rate + degree_offset)) - (boost_y - boost_center_y) * math.sin(math.radians(boost * spin_rate + degree_offset))) * scale,
                  (boost_center_y + (boost_x - boost_center_x) * math.sin(math.radians(boost * spin_rate + degree_offset)) + (boost_y - boost_center_y) * math.cos(math.radians(boost * spin_rate + degree_offset))) * scale)

    ac.ext_glTexCoord2f(1, 0)
    ac.glVertex2f((boost_center_x + (boost_x + boost_width - boost_center_x) * math.cos(math.radians(boost * spin_rate + degree_offset)) - (boost_y - boost_center_y) * math.sin(math.radians(boost * spin_rate + degree_offset))) * scale,
                  (boost_center_y + (boost_x + boost_width - boost_center_x) * math.sin(math.radians(boost * spin_rate + degree_offset)) + (boost_y - boost_center_y) * math.cos(math.radians(boost * spin_rate + degree_offset))) * scale)

    ac.ext_glTexCoord2f(1, 1)
    ac.glVertex2f((boost_center_x + (boost_x + boost_width - boost_center_x) * math.cos(math.radians(boost * spin_rate + degree_offset)) - (boost_y + boost_height - boost_center_y) * math.sin(math.radians(boost * spin_rate + degree_offset))) * scale,
                  (boost_center_y + (boost_x + boost_width - boost_center_x) * math.sin(math.radians(boost * spin_rate + degree_offset)) + (boost_y + boost_height - boost_center_y) * math.cos(math.radians(boost * spin_rate + degree_offset))) * scale)

    ac.ext_glTexCoord2f(0, 1)
    ac.glVertex2f((boost_center_x + (boost_x - boost_center_x) * math.cos(math.radians(boost * spin_rate + degree_offset)) - (boost_y + boost_height - boost_center_y) * math.sin(math.radians(boost * spin_rate + degree_offset))) * scale,
                  (boost_center_y + (boost_x - boost_center_x) * math.sin(math.radians(boost * spin_rate + degree_offset)) + (boost_y + boost_height - boost_center_y) * math.cos(math.radians(boost * spin_rate + degree_offset))) * scale)

    ac.glEnd()


# Settings window
def settings_window_activated(*args):
    global settings_window_visibility

    settings_window_visibility = 1


def settings_window_deactivated(*args):
    global settings_window_visibility

    settings_window_visibility = 0


# Settings window listeners
def theme_spinner_clicked(*args):
    global config, update_config, preview_label

    update_config = True
    ac.setBackgroundTexture(preview_label,
                            app_path + "themes/D" + "{:.0f}".format(ac.getValue(theme_spinner)) + "/preview.png")

    config.set("D Turbo", "theme", "{:.0f}".format(ac.getValue(theme_spinner)))


# Settings window listeners
def scale_spinner_clicked(*args):
    global config, update_config, scale

    update_config = True
    scale = ac.getValue(scale_spinner) / 100

    config.set("D Turbo", "scale", str(ac.getValue(scale_spinner)))


def unit_bar_checkbox_clicked(*args):
    global config, update_config, unit_bar, spin_rate

    update_config = True

    if unit_bar:
        unit_bar = False
    else:
        unit_bar = True

    config.set("D Turbo", "unit_bar", str(unit_bar))


def refresh_rate_checkbox_clicked(*args):
    global config, update_config, lower_refresh_rate

    update_config = True

    if lower_refresh_rate:
        lower_refresh_rate = False
    else:
        lower_refresh_rate = True

    config.set("D Turbo", "lower_refresh_rate", str(lower_refresh_rate))


def turbo_amount_spinner_clicked(*args):
    global config, update_config, turbo_amount

    update_config = True

    turbo_amount = ac.getValue(turbo_amount_spinner)

    config.set("D Turbo", "turbo_amount", "{:.0f}".format(ac.getValue(turbo_amount_spinner)))


def acUpdate(deltaT):
    global timer, timer2, current_car, boost, get_headlights

    timer += deltaT
    if lower_refresh_rate:
        timer2 += deltaT

    if timer > 0.1:
        timer = 0
        current_car = ac.getFocusedCar()
        get_headlights = ac.ext_getHeadlights(current_car)
        ac.setBackgroundOpacity(app_window, 0)

    if lower_refresh_rate:
        if timer2 > 0.0333:
            timer2 = 0
            boost = ac.getCarState(current_car, acsys.CS.TurboBoost) / turbo_amount
    else:
        boost = ac.getCarState(current_car, acsys.CS.TurboBoost) / turbo_amount


def acShutdown():
    global config, update_config, config_path

    # Update config if needed
    if update_config:
        with open(config_path, 'w') as file_config:
            config.write(file_config)
