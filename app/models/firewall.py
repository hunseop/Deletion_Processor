class Firewall:
    def __init__(self):
        self.vendor = None
        self.primary_ip = None
        self.secondary_ip = None
        self.username = None
        self.password = None

    def to_dict(self):
        return {
            'vendor': self.vendor,
            'primary_ip': self.primary_ip,
            'secondary_ip': self.secondary_ip,
            'username': self.username
        } 