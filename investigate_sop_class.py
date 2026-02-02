"""Investigate pynetdicom 3.x SOP class structure."""

from pynetdicom import sop_class
import inspect

print("Investigating pynetdicom sop_class module structure")
print("=" * 70)

# Get all attributes
all_attrs = dir(sop_class)
print(f"Total attributes in sop_class: {len(all_attrs)}")

# Filter to classes only
classes = [attr for attr in all_attrs if not attr.startswith('_') and inspect.isclass(getattr(sop_class, attr))]
print(f"Classes (non-private): {len(classes)}")

# Sample first 10 classes
print("\nFirst 10 classes:")
for i, attr_name in enumerate(classes[:10]):
    obj = getattr(sop_class, attr_name)
    has_uid = hasattr(obj, 'uid')
    print(f"  {i+1}. {attr_name}")
    print(f"     - Is class: {inspect.isclass(obj)}")
    print(f"     - Has 'uid': {has_uid}")
    if has_uid:
        try:
            uid_val = obj.uid
            print(f"     - UID value: {uid_val}")
            print(f"     - UID type: {type(uid_val)}")
        except Exception as e:
            print(f"     - Error getting UID: {e}")

# Try to understand the actual structure
print("\n" + "=" * 70)
print("Analyzing SecondaryCaptureImageStorage as example:")
try:
    from pynetdicom.sop_class import SecondaryCaptureImageStorage
    print(f"  Class: {SecondaryCaptureImageStorage}")
    print(f"  Type: {type(SecondaryCaptureImageStorage)}")
    print(f"  Has uid: {hasattr(SecondaryCaptureImageStorage, 'uid')}")
    if hasattr(SecondaryCaptureImageStorage, 'uid'):
        print(f"  UID: {SecondaryCaptureImageStorage.uid}")
        print(f"  UID str: {str(SecondaryCaptureImageStorage.uid)}")
except Exception as e:
    print(f"  Error: {e}")

# Check all different potential UID storage methods
print("\n" + "=" * 70)
print("Checking different UID attribute names:")
test_attrs = ['uid', 'UID', '_uid', '__uid__', 'sopClassUID', 'sop_class_uid']
for attr_name in classes[:5]:
    obj = getattr(sop_class, attr_name)
    print(f"\n{attr_name}:")
    for uid_attr in test_attrs:
        if hasattr(obj, uid_attr):
            try:
                val = getattr(obj, uid_attr)
                print(f"  ? {uid_attr}: {val}")
            except Exception as e:
                print(f"  ? {uid_attr}: {e}")
