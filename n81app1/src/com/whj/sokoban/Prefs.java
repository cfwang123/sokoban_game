package com.whj.sokoban;

import javax.microedition.rms.RecordStore;
import javax.microedition.rms.RecordStoreException;

/**
 * 用 RMS（Record Management System）记住上次关卡。
 * <p>
 * 对应 Android SharedPreferences / iOS UserDefaults。
 * N81 等 S60 手机上 RMS 是标准 MIDP 本地小存储。
 */
public final class Prefs {
    private static final String RS_NAME = "sokoban_n81";

    private Prefs() {}

    public static int loadLastLevel() {
        RecordStore rs = null;
        try {
            rs = RecordStore.openRecordStore(RS_NAME, true);
            if (rs.getNumRecords() < 1) {
                return 0;
            }
            byte[] data = rs.getRecord(1);
            if (data == null || data.length < 1) {
                return 0;
            }
            int v = data[0] & 0xFF;
            if (v >= LevelsData.COUNT) {
                return 0;
            }
            return v;
        } catch (Exception e) {
            return 0;
        } finally {
            closeQuietly(rs);
        }
    }

    public static void saveLastLevel(int index) {
        if (index < 0) {
            index = 0;
        }
        if (index >= LevelsData.COUNT) {
            index = LevelsData.COUNT - 1;
        }
        RecordStore rs = null;
        try {
            rs = RecordStore.openRecordStore(RS_NAME, true);
            byte[] data = new byte[] { (byte) index };
            if (rs.getNumRecords() < 1) {
                rs.addRecord(data, 0, data.length);
            } else {
                rs.setRecord(1, data, 0, data.length);
            }
        } catch (Exception e) {
            // 演示程序忽略存储失败
        } finally {
            closeQuietly(rs);
        }
    }

    private static void closeQuietly(RecordStore rs) {
        if (rs != null) {
            try {
                rs.closeRecordStore();
            } catch (RecordStoreException e) {
                // ignore
            }
        }
    }
}
