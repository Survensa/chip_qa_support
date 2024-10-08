from dataclasses import dataclass


@dataclass
class Cluster:
    ACE: str = "Access_Control_Enforcement.yaml"
    ACL: str = "Access_Control.yaml"
    ACFREMON: str = "Activated_Carbon_Filter_Monitoring.yaml"
    AIRQUAL: str = "Air_Quality.yaml"
    BIND: str = "Binding.yaml"
    BINFO: str = "Basic_Information.yaml"
    BOOL: str = "Boolean.yaml"
    BRBINFO: str = "Bridged_Device_Basic_Information.yaml"
    CDOCONC: str = "Carbon_Dioxide_Concentration_Measurement.yaml"
    CC: str = "Color_Control.yaml"
    CMOCONC: str = "Carbon_Monoxide_Concentration_Measurement.yaml"
    DESC: str = "Descriptor_Cluster.yaml"
    DGGEN: str = "Gendiag.yaml"
    DGTHREAD: str = "Thread_diag.yaml"
    DGWIFI: str = "Wifi_Diag.yaml"
    DGETH: str = "Ethernet_Diag.yaml"
    DGSW: str = "Software_Diag.yaml"
    DISHALM: str = "Dishwasher_Alarm_Cluster.yaml"
    DISHM: str = "Dishwasher_Mode_Cluster.yaml"
    DRLK: str = "Door_lock.yaml"
    FLABEL: str = "Fixed_Lable.yaml"
    FLDCONC: str = "Formaldehyde_Concentration_Measurement.yaml"
    FAN: str = "Fan_Control.yaml"
    FLW: str = "Flow_Measurement_Cluster.yaml"
    G: str = "Groups.yaml"
    GRPKEY: str = "Group_Communication.yaml"
    HEPAFREMON: str = "HEPA_Filter_Monitoring.yaml"
    I: str = "Identify.yaml"
    ILL: str = "Illuminance_Measurement_Cluster.yaml"
    LCFG: str = "Localization_Configuration_cluster.yaml"
    LTIME: str = "Time_Format_localization.yaml"
    LUNIT: str = "Unit_localization.yaml"
    LVL: str = "Level_Control.yaml"
    LWM: str = "Laundry_Washer_Mode.yaml"
    MC: str = "Media.yaml"
    MOD: str = "Mode_Select.yaml"
    NDOCONC: str = "Nitrogen_Dioxide_Concentration_Measurement.yaml"
    OCC: str = "OccupancySensing.yaml"
    OZCONC: str = "Ozone_Concentration_Measurement.yaml"
    OO: str = "OnOff.yaml"
    PCC: str = "pump_configuration.yaml"
    PMHCONC: str = "PM1_Concentration_Measurement.yaml"
    PMICONC: str = "PM2.5_Concentration_Measurement.yaml"
    PMKCONC: str = "PM10_Concentration_Measurement.yaml"
    PRS: str = "Pressure_measurement.yaml"
    PS: str = "Power_Source_Cluster.yaml"
    PSCFG: str = "Power_Source_Configuration.yaml"
    RNCONC: str = "Radon_Concentration_Measurement.yaml"
    RVCCLEANM: str = "RVC_Clean_Mode.yaml"
    RVCRUNM: str = "RVC_Run_Mode.yaml"
    RH: str = "Relative_Humidity_Measurement_Cluster.yaml"
    SMOKECO: str = "Smoke_and_CO_Alarm.yaml"
    SMOKECO: str = "Smoke_and_CO_Alarm.yaml"
    SWTCH: str = "Switch.yaml"
    TCCM: str = "Refrigerator_And_Temperature_Controlled_Cabinet_Mode.yaml"
    TMP: str = "Temperature_Measurement_Cluster.yaml"
    TSUIC: str = "Thermostat_User.yaml"
    TSTAT: str = "Thermostat.yaml"
    TVOCCONC: str = "Total_Volatile_Organic_Compounds_Concentration_Measurement.yaml"
    ULABEL: str = "User_Lable.yaml"
    WASHERTCTRL: str = "Washer_Control.yaml"
    WNCV: str = "Window_Covering.yaml"
