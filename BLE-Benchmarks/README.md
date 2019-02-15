# BLE-Benchmarks
Suite of benchmarking apps (DroidBench refactor) for testing the presence of cryptography with Bluetooth Low Energy in Android APKs.

## Comparison of execution results: BLECryptracer vs. Amandroid

### Reads
| Task                        | Leaks             | Detected     | Notes          | Amandroid | Amandroid Notes |
|-----------------------------|-------------------|--------------|----------------|-----------|-----------------|
| Merge1                      | 0                 | Yes [HIGH]   | False Positive | Yes       | False Positive  |
| ApplicationModeling1        | 1                 | Yes [HIGH]   | True Positive  | No        | False Negative  |
| DirectLeak1                 | 1                 | Yes [HIGH]   | True Positive  | Yes       | True Positive   |
| Library2                    | 1                 | Yes [HIGH]   | True Positive  | Yes       | True Positive   |
| LogNoLeak                   | 0                 | No           | True Negative  | No        | True Negative   |
| Obfuscation1                | 1                 | Yes [HIGH]   | True Positive  | Yes       | True Positive   |
| Parcel1                     | 1                 | Yes [HIGH]   | True Positive  | No        | False Negative  |
| PrivateDataLeak1            | 1                 | Yes [HIGH]   | True Positive  | Yes       | True Positive   |
| PublicAPIField1             | 1                 | Yes [LOW]    | True Positive  | Yes       | True Positive   |
| PublicAPIField2             | 1                 | Yes [MEDIUM] | True Positive  | Yes       | True Positive   |
| ArrayAccess1                | 0                 | Yes [LOW]    | False Positive | Yes       | False Positive  |
| ArrayAccess2                | 0                 | Yes [LOW]    | False Positive | Yes       | False Positive  |
| ArrayCopy1                  | 1                 | Yes [LOW]    | True Positive  | No        | False Negative  |
| ArrayToString1              | 1                 | Yes [HIGH]   | True Positive  | No        | False Negative  |
| HashMapAccess1              | 0                 | Yes [MEDIUM] | False Positive | Yes       | False Positive  |
| ListAccess1                 | 0                 | Yes [LOW]    | False Positive | Yes       | False Positive  |
| MultidimensionalArray1      | 1                 | Yes [LOW]    | True Positive  | Yes       | True Positive   |
| AnonymousClass1             | 1                 | Yes [HIGH]   | True Positive  | No        | False Negative  |
| Button1                     | 1                 | Yes [HIGH]   | True Positive  | Yes       | True Positive   |
| Button2                     | 1                 | Yes [HIGH]   | True Positive  | Yes       | True Positive   |
| Button3                     | 1                 | Yes [HIGH]   | True Positive  | No        | False Negative  |
| Button4                     | 1                 | Yes [HIGH]   | True Positive  | No        | False Negative  |
| Button5                     | 1                 | Yes [LOW]    | True Positive  | No        | False Negative  |
| LocationLeak1               | 1                 | Yes [HIGH]   | True Positive  | No        | False Negative  |
| LocationLeak2               | 1                 | Yes [HIGH]   | True Positive  | No        | False Negative  |
| LocationLeak3               | 1                 | Yes [MEDIUM] | True Positive  | No        | False Negative  |
| MethodOverride1             | 1                 | Yes [HIGH]   | True Positive  | Yes       | True Positive   |
| MultiHandlers1              | 0                 | Yes [MEDIUM] | False Positive | No        | True Negative   |
| Ordering1                   | 0                 | Yes [HIGH]   | False Positive | No        | True Negative   |
| RegisterGlobal1             | 1                 | Yes [HIGH]   | True Positive  | No        | False Negative  |
| RegisterGlobal2             | 1                 | Yes [HIGH]   | True Positive  | No        | False Negative  |
| FieldSensitivity1           | 0                 | Yes [MEDIUM] | False Positive | No        | True Negative   |
| FieldSensitivity2           | 0                 | Yes [MEDIUM] | False Positive | No        | True Negative   |
| FieldSensitivity3           | 1                 | Yes [HIGH]   | True Positive  | Yes       | True Positive   |
| FieldSensitivity4           | 0                 | Yes [HIGH]   | False Positive | No        | True Negative   |
| InheritedObjects1           | 1                 | Yes [MEDIUM] | True Positive  | Yes       | True Positive   |
| ObjectSensitivity1          | 0                 | Yes [LOW]    | False Positive | No        | True Negative   |
| ObjectSensitivity2          | 0                 | Yes [HIGH]   | False Positive | No        | True Negative   |
| Clone1                      | 1                 | Yes [MEDIUM] | True Positive  | Yes       | True Positive   |
| Loop1                       | 1                 | Yes [HIGH]   | True Positive  | Yes       | True Positive   |
| Loop2                       | 1                 | Yes [HIGH]   | True Positive  | Yes       | True Positive   |
| SourceCodeSpecific1         | 1                 | Yes [HIGH]   | True Positive  | Yes       | True Positive   |
| StartProcessWithSecret1     | 1                 | Yes [HIGH]   | True Positive  | Yes       | True Positive   |
| StaticInitialization1       | 1                 | Yes [HIGH]   | True Positive  | No        | False Negative  |
| StaticInitialization2       | 1                 | Yes [HIGH]   | True Positive  | No        | False Negative  |
| StaticInitialization3       | 1                 | Yes [HIGH]   | True Positive  | No        | False Negative  |
| StringFormatter1            | 1                 | Yes [LOW]    | True Positive  | No        | False Negative  |
| StringPatternMatching1      | 1                 | Yes [HIGH]   | True Positive  | Yes       | True Positive   |
| StringToCharArray1          | 1                 | Yes [LOW]    | True Positive  | Yes       | True Positive   |
| StringToOutputStream1       | 1                 | Yes [MEDIUM] | True Positive  | Yes       | True Positive   |
| VirtualDispatch1            | 1                 | Yes [HIGH]   | True Positive  | Yes       | True Positive   |
| VirtualDispatch2            | 1 (another false) | Yes [MEDIUM] | True Positive  | Yes       | True Positive   |
| VirtualDispatch3            | 0                 | No           | True Negative  | No        | True Negative   |
| VirtualDispatch4            | 0                 | No           | True Negative  | No        | True Negative   |
| ImplicitFlow1               | 2                 | Yes [HIGH]   | True Positive  | No        | False Negative  |
| ActivityCommunication1      | 1                 | Yes [HIGH]   | True Positive  | Yes       | True Positive   |
| ActivityCommunication2      | 1                 | Yes [HIGH]   | True Positive  | Yes       | True Positive   |
| ActivityCommunication3      | 1                 | Yes [HIGH]   | True Positive  | Yes       | True Positive   |
| ActivityCommunication4      | 1                 | Yes [HIGH]   | True Positive  | Yes       | True Positive   |
| ActivityCommunication5      | 1                 | Yes [HIGH]   | True Positive  | Yes       | True Positive   |
| ActivityCommunication6      | 1                 | Yes [HIGH]   | True Positive  | Yes       | True Positive   |
| ActivityCommunication7      | 1                 | Yes [HIGH]   | True Positive  | Yes       | True Positive   |
| ActivityCommunication8      | 1                 | Yes [HIGH]   | True Positive  | Yes       | True Positive   |
| BroadcastTaintAndLeak1      | 1                 | Yes [HIGH]   | True Positive  | Yes       | True Positive   |
| ServiceCommunication1       | 1                 | No           | False Negative | Yes       | True Positive   |
| Singletons1                 | 1                 | Yes [HIGH]   | True Positive  | No        | False Negative  |
| UnresolvableIntent1         | 2                 | Yes [HIGH]   | True Positive  | Yes       | True Positive   |
| ActivityLifecycle1          | 1                 | Yes [HIGH]   | True Positive  | Yes       | True Positive   |
| ActivityLifecycle2          | 1                 | No           | False Negative | No        | False Negative  |
| ActivityLifecycle3          | 1                 | Yes [HIGH]   | True Positive  | No        | False Negative  |
| ActivityLifecycle4          | 1                 | Yes [HIGH]   | True Positive  | Yes       | True Positive   |
| ActivitySavedState1         | 1                 | Yes [HIGH]   | True Positive  | No        | False Negative  |
| ApplicationLifecycle1       | 1                 | Yes [HIGH]   | True Positive  | No        | False Negative  |
| ApplicationLifecycle2       | 1                 | Yes [HIGH]   | True Positive  | No        | False Negative  |
| ApplicationLifecycle3       | 1                 | Yes [HIGH]   | True Positive  | No        | False Negative  |
| AsynchronousEventOrdering1  | 1                 | Yes [HIGH]   | True Positive  | Yes       | True Positive   |
| BroadcastReceiverLifecycle1 | 1                 | Yes [HIGH]   | True Positive  | Yes       | True Positive   |
| BroadcastReceiverLifecycle2 | 1                 | Yes [HIGH]   | True Positive  | No        | False Negative  |
| EventOrdering1              | 1                 | Yes [HIGH]   | True Positive  | No        | False Negative  |
| FragmentLifecycle1          | 1                 | Yes [HIGH]   | True Positive  | Yes       | True Positive   |
| FragmentLifecycle2          | 1                 | Yes [MEDIUM] | True Positive  | No        | False Negative  |
| ServiceLifecycle1           | 1                 | Yes [HIGH]   | True Positive  | Yes       | True Positive   |
| ServiceLifecycle2           | 1                 | Yes [HIGH]   | True Positive  | No        | False Negative  |
| Reflection1                 | 1                 | Yes [HIGH]   | True Positive  | Yes       | True Positive   |
| Reflection2                 | 1                 | Yes [LOW]    | True Positive  | No        | False Negative  |
| Reflection3                 | 1                 | Yes [LOW]    | True Positive  | No        | False Negative  |
| Reflection4                 | 1                 | No           | False Negative | No        | False Negative  |
| Threading                                                                                                     |
| AsyncTask1                  | 1                 | Yes [HIGH]   | True Positive  | Yes       | True Positive   |
| Executor1                   | 1                 | Yes [HIGH]   | True Positive  | Yes       | True Positive   |
| JavaThread1                 | 1                 | Yes [HIGH]   | True Positive  | Yes       | True Positive   |
| JavaThread2                 | 1                 | Yes [HIGH]   | True Positive  | Yes       | True Positive   |
| Looper1                     | 1                 | No           | False Negative | No        | False Negative  |

### Writes
| Task                        | Leaks             | Detected     | Notes          | Amandroid | Amandroid Notes |
|-----------------------------|-------------------|--------------|----------------|-----------|-----------------|
| Merge1                      | 0                 | Yes [HIGH]   | False Positive | Yes       | False Positive  |
| ApplicationModeling1        | 1                 | Yes [HIGH]   | True Positive  | No        | False Negative  |
| DirectLeak1                 | 1                 | Yes [HIGH]   | True Positive  | Yes       | True Positive   |
| Library2                    | 1                 | Yes [HIGH]   | True Positive  | Yes       | True Positive   |
| LogNoLeak                   | 0                 | No           | True Negative  | No        | True Negative   |
| Obfuscation1                | 1                 | Yes [HIGH]   | True Positive  | No        | False Negative  |
| Parcel1                     | 1                 | Yes [HIGH]   | True Positive  | No        | False Negative  |
| PrivateDataLeak1            | 1                 | Yes [MEDIUM] | True Positive  | Yes       | True Positive   |
| PublicAPIField1             | 1                 | Yes [LOW]    | True Positive  | Yes       | True Positive   |
| PublicAPIField2             | 1                 | Yes [MEDIUM] | True Positive  | Yes       | True Positive   |
| ArrayAccess1                | 0                 | Yes [LOW]    | False Positive | Yes       | False Positive  |
| ArrayAccess2                | 0                 | Yes [LOW]    | False Positive | Yes       | False Positive  |
| ArrayCopy1                  | 1                 | Yes [MEDIUM] | True Positive  | No        | False Negative  |
| ArrayToString1              | 1                 | Yes [MEDIUM] | True Positive  | No        | False Negative  |
| HashMapAccess1              | 0                 | Yes [MEDIUM] | False Positive | Yes       | False Positive  |
| ListAccess1                 | 0                 | Yes [LOW]    | False Positive | Yes       | False Positive  |
| MultidimensionalArray1      | 1                 | Yes [LOW]    | True Positive  | Yes       | True Positive   |
| AnonymousClass1             | 1                 | Yes [HIGH]   | True Positive  | Yes       | True Positive   |
| Button1                     | 1                 | Yes [HIGH]   | True Positive  | Yes       | True Positive   |
| Button2                     | 1                 | Yes [HIGH]   | True Positive  | Yes       | True Positive   |
| Button3                     | 1                 | Yes [HIGH]   | True Positive  | No        | False Negative  |
| Button4                     | 1                 | Yes [HIGH]   | True Positive  | No        | False Negative  |
| Button5                     | 1                 | No           | False Negative | No        | False Negative  |
| LocationLeak1               | 1                 | Yes [HIGH]   | True Positive  | Yes       | True Positive   |
| LocationLeak2               | 1                 | Yes [HIGH]   | True Positive  | Yes       | True Positive   |
| LocationLeak3               | 1                 | Yes [MEDIUM] | True Positive  | Yes       | True Positive   |
| MethodOverride1             | 1                 | Yes [HIGH]   | True Positive  | Yes       | True Positive   |
| MultiHandlers1              | 0                 | Yes [MEDIUM] | False Positive | Yes       | False Positive  |
| Ordering1                   | 0                 | Yes [HIGH]   | False Positive | Yes       | False Positive  |
| RegisterGlobal1             | 1                 | Yes [HIGH]   | True Positive  | No        | False Negative  |
| RegisterGlobal2             | 1                 | Yes [HIGH]   | True Positive  | No        | False Negative  |
| FieldSensitivity1           | 0                 | Yes [LOW]    | False Positive | No        | True Negative   |
| FieldSensitivity2           | 0                 | Yes [MEDIUM] | False Positive | No        | True Negative   |
| FieldSensitivity3           | 1                 | Yes [HIGH]   | True Positive  | Yes       | True Positive   |
| FieldSensitivity4           | 0                 | Yes [HIGH]   | False Positive | No        | True Negative   |
| InheritedObjects1           | 1                 | Yes [MEDIUM] | True Positive  | Yes       | True Positive   |
| ObjectSensitivity1          | 0                 | Yes [LOW]    | False Positive | No        | True Negative   |
| ObjectSensitivity2          | 0                 | Yes [HIGH]   | False Positive | No        | True Negative   |
| Clone1                      | 1                 | Yes [MEDIUM] | True Positive  | Yes       | True Positive   |
| Loop1                       | 1                 | Yes [MEDIUM] | True Positive  | Yes       | True Positive   |
| Loop2                       | 1                 | Yes [MEDIUM] | True Positive  | Yes       | True Positive   |
| SourceCodeSpecific1         | 1                 | Yes [LOW]    | True Positive  | No        | False Negative  |
| StartProcessWithSecret1     | 1                 | Yes [HIGH]   | True Positive  | Yes       | True Positive   |
| StaticInitialization1       | 1                 | Yes [MEDIUM] | True Positive  | No        | False Negative  |
| StaticInitialization2       | 1                 | Yes [MEDIUM] | True Positive  | No        | False Negative  |
| StaticInitialization3       | 1                 | Yes [MEDIUM] | True Positive  | No        | False Negative  |
| StringFormatter1            | 1                 | Yes [LOW]    | True Positive  | No        | False Negative  |
| StringPatternMatching1      | 1                 | Yes [MEDIUM] | True Positive  | Yes       | True Positive   |
| StringToCharArray1          | 1                 | Yes [MEDIUM] | True Positive  | Yes       | True Positive   |
| StringToOutputStream1       | 1                 | Yes [MEDIUM] | True Positive  | Yes       | True Positive   |
| VirtualDispatch1            | 1                 | Yes [MEDIUM] | True Positive  | Yes       | True Positive   |
| VirtualDispatch2            | 1 (another false) | No           | False Negative | No        | False Negative  |
| VirtualDispatch3            | 0                 | No           | True Negative  | No        | True Negative   |
| VirtualDispatch4            | 0                 | No           | True Negative  | No        | True Negative   |
| ImplicitFlow1               | 2                 | Yes [MEDIUM] | True Positive  | No        | False Negative  |
| ActivityCommunication1      | 1                 | Yes [HIGH]   | True Positive  | Yes       | True Positive   |
| ActivityCommunication2      | 1                 | Yes [HIGH]   | True Positive  | Yes       | True Positive   |
| ActivityCommunication3      | 1                 | Yes [HIGH]   | True Positive  | Yes       | True Positive   |
| ActivityCommunication4      | 1                 | Yes [HIGH]   | True Positive  | Yes       | True Positive   |
| ActivityCommunication5      | 1                 | Yes [HIGH]   | True Positive  | Yes       | True Positive   |
| ActivityCommunication6      | 1                 | Yes [HIGH]   | True Positive  | Yes       | True Positive   |
| ActivityCommunication7      | 1                 | Yes [HIGH]   | True Positive  | Yes       | True Positive   |
| ActivityCommunication8      | 1                 | Yes [HIGH]   | True Positive  | Yes       | True Positive   |
| BroadcastTaintAndLeak1      | 1                 | Yes [HIGH]   | True Positive  | Yes       | True Positive   |
| ServiceCommunication1       | 1                 | No           | False Negative | Yes       | True Positive   |
| Singletons1                 | 1                 | Yes [HIGH]   | True Positive  | No        | False Negative  |
| UnresolvableIntent1         | 1                 | Yes [HIGH]   | True Positive  | Yes       | True Positive   |
| ActivityLifecycle1          | 1                 | Yes [HIGH]   | True Positive  | Yes       | True Positive   |
| ActivityLifecycle2          | 1                 | No           | False Negative | No        | False Negative  |
| ActivityLifecycle3          | 1                 | Yes [HIGH]   | True Positive  | Yes       | True Positive   |
| ActivityLifecycle4          | 1                 | Yes [HIGH]   | True Positive  | Yes       | True Positive   |
| ActivitySavedState1         | 1                 | Yes [MEDIUM] | True Positive  | Yes       | True Positive   |
| ApplicationLifecycle1       | 1                 | Yes [HIGH]   | True Positive  | No        | False Negative  |
| ApplicationLifecycle2       | 1                 | Yes [HIGH]   | True Positive  | No        | False Negative  |
| ApplicationLifecycle3       | 1                 | Yes [HIGH]   | True Positive  | No        | False Negative  |
| AsynchronousEventOrdering1  | 1                 | Yes [HIGH]   | True Positive  | Yes       | True Positive   |
| BroadcastReceiverLifecycle1 | 1                 | Yes [HIGH]   | True Positive  | Yes       | True Positive   |
| BroadcastReceiverLifecycle2 | 1                 | Yes [HIGH]   | True Positive  | No        | False Negative  |
| EventOrdering1              | 1                 | Yes [HIGH]   | True Positive  | Yes       | True Positive   |
| FragmentLifecycle1          | 1                 | Yes [HIGH]   | True Positive  | Yes       | True Positive   |
| FragmentLifecycle2          | 1                 | Yes [MEDIUM] | True Positive  | No        | False Negative  |
| ServiceLifecycle1           | 1                 | Yes [HIGH]   | True Positive  | Yes       | True Positive   |
| ServiceLifecycle2           | 1                 | Yes [HIGH]   | True Positive  | Yes       | True Positive   |
| Reflection1                 | 1                 | Yes [HIGH]   | True Positive  | Yes       | True Positive   |
| Reflection2                 | 1                 | Yes [LOW]    | True Positive  | No        | False Negative  |
| Reflection3                 | 1                 | Yes [MEDIUM] | True Positive  | No        | False Negative  |
| Reflection4                 | 1                 | No           | False Negative | No        | False Negative  |
| AsyncTask1                  | 1                 | No           | False Negative | Yes       | True Positive   |
| Executor1                   | 1                 | Yes [HIGH]   | True Positive  | Yes       | True Positive   |
| JavaThread1                 | 1                 | Yes [HIGH]   | True Positive  | Yes       | True Positive   |
| JavaThread2                 | 1                 | Yes [HIGH]   | True Positive  | Yes       | True Positive   |
| Looper1                     | 1                 | No           | False Negative | No        | False Negative  |

## Notes
* These APKs will not work if installed on a device.
* Certain test cases have been excluded (when found to be irrelevant).