package android.view;

import android.os.IInterface;
import android.os.RemoteException;

public interface IWindowManager extends IInterface {
    int watchRotation(IRotationWatcher watcher, int displayId) throws RemoteException;
    void removeRotationWatcher(IRotationWatcher watcher) throws RemoteException;
}
