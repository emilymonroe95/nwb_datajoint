import datajoint as dj

from .common_ephys import Raw
from .common_interval import IntervalList  # noqa: F401
from .common_nwbfile import Nwbfile
from .common_session import Session  # noqa: F401
from .nwb_helper_fn import get_data_interface, get_nwb_file
from .dj_helper_fn import fetch_nwb  # dj_replace

schema = dj.schema('common_dio')


@schema
class DIOEvents(dj.Imported):
    definition = """
    -> Session
    dio_event_name: varchar(80)  # the name assigned to this DIO event
    ---
    dio_object_id: varchar(80)   # the object id of the data in the NWB file
    -> IntervalList              # the list of intervals for this object
    """

    def make(self, key):
        nwb_file_name = key['nwb_file_name']
        nwb_file_abspath = Nwbfile.get_abs_path(nwb_file_name)
        nwbf = get_nwb_file(nwb_file_abspath)

        behav_events = get_data_interface(nwbf, 'behavioral_events')
        if behav_events is None:
            print(
                f'No behavioral events data interface found in {nwb_file_name}\n')
            return

        behav_events_ts = behav_events.time_series
        # the times for these events correspond to the valid times for the raw data
        key['interval_list_name'] = (
            Raw() & {'nwb_file_name': nwb_file_name}).fetch1('interval_list_name')
        for event_series in behav_events_ts:
            key['dio_event_name'] = event_series
            key['dio_object_id'] = behav_events_ts[event_series].object_id
            self.insert1(key, skip_duplicates=True)

    def fetch_nwb(self, *attrs, **kwargs):
        return fetch_nwb(self, (Nwbfile, 'nwb_file_abs_path'), *attrs, **kwargs)