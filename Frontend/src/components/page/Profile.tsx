import { User, Mail, Phone, CreditCard, Bell, Lock, HelpCircle, LogOut, ChevronRight } from 'lucide-react';

interface ProfileProps {
  userData: {
    name: string;
    ic: string;
    monthlySalary: number;
  };
}

export function Profile({ userData }: ProfileProps) {
  const menuItems = [
    {
      section: 'Account',
      items: [
        { icon: User, label: 'Personal Information', value: userData.name || 'Not set' },
        { icon: Mail, label: 'Email', value: 'user@example.com' },
        { icon: Phone, label: 'Phone Number', value: '+60123456789' },
        { icon: CreditCard, label: 'IC Number', value: userData.ic || 'Not verified' },
      ],
    },
    {
      section: 'Preferences',
      items: [
        { icon: Bell, label: 'Notifications', value: 'Enabled' },
        { icon: Lock, label: 'Security & Privacy', value: '' },
      ],
    },
    {
      section: 'Support',
      items: [
        { icon: HelpCircle, label: 'Help & Support', value: '' },
      ],
    },
  ];

  return (
    <div className="min-h-screen bg-gray-50 pb-24">
      <div className="bg-gradient-to-b from-indigo-600 to-indigo-800 text-white p-6 pb-12 rounded-b-3xl">
        <h1 className="text-2xl mb-6">Profile Settings</h1>
        
        <div className="flex items-center gap-4">
          <div className="w-20 h-20 bg-white/20 rounded-full flex items-center justify-center text-3xl">
            👤
          </div>
          <div>
            <h2 className="text-xl mb-1">{userData.name || 'User Name'}</h2>
            <p className="text-indigo-200">Basic Member</p>
          </div>
        </div>
      </div>

      <div className="p-6 -mt-6">
        <div className="bg-white rounded-2xl p-6 shadow-sm mb-6">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-gray-600 text-sm mb-1">Monthly Salary</p>
              <p className="text-xl">RM {userData.monthlySalary}</p>
            </div>
            <div>
              <p className="text-gray-600 text-sm mb-1">Member Since</p>
              <p className="text-xl">Dec 2024</p>
            </div>
          </div>
        </div>

        {menuItems.map((section, sectionIndex) => (
          <div key={sectionIndex} className="mb-6">
            <h3 className="text-sm text-gray-600 mb-3 px-2">{section.section}</h3>
            <div className="bg-white rounded-2xl overflow-hidden shadow-sm">
              {section.items.map((item, itemIndex) => {
                const Icon = item.icon;
                return (
                  <button
                    key={itemIndex}
                    className="w-full flex items-center gap-4 p-4 hover:bg-gray-50 transition-colors border-b border-gray-100 last:border-b-0"
                  >
                    <Icon className="w-5 h-5 text-gray-600" />
                    <div className="flex-1 text-left">
                      <p className="text-gray-900">{item.label}</p>
                      {item.value && (
                        <p className="text-sm text-gray-500">{item.value}</p>
                      )}
                    </div>
                    <ChevronRight className="w-5 h-5 text-gray-400" />
                  </button>
                );
              })}
            </div>
          </div>
        ))}

        <div className="bg-white rounded-2xl overflow-hidden shadow-sm">
          <button className="w-full flex items-center gap-4 p-4 hover:bg-red-50 transition-colors text-red-600">
            <LogOut className="w-5 h-5" />
            <span>Log Out</span>
          </button>
        </div>

        <div className="mt-8 text-center text-sm text-gray-500">
          <p>Version 1.0.0</p>
          <p className="mt-1">© 2024 Early Wage Access</p>
        </div>
      </div>
    </div>
  );
}
