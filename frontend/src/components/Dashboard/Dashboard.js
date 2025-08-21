import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { FiLogOut, FiUser, FiImage, FiEdit3, FiDownload, FiUpload, FiSettings } from 'react-icons/fi';
import toast from 'react-hot-toast';

const Dashboard = () => {
    const [user, setUser] = useState(null);
    const [recentDrawings, setRecentDrawings] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        const userData = localStorage.getItem('user');
        if (userData) {
            setUser(JSON.parse(userData));
        }
        setIsLoading(false);
    }, []);

    const handleLogout = () => {
        localStorage.removeItem('user');
        localStorage.removeItem('user_id');
        toast.success('Logged out successfully');
        navigate('/login');
    };

    const features = [
        {
            title: 'Drawing Canvas',
            description: 'Create beautiful drawings with our advanced canvas tools',
            icon: <FiEdit3 className="w-8 h-8" />,
            path: '/drawing',
            color: 'bg-blue-500'
        },
        {
            title: 'Image to Sketch',
            description: 'Convert images to sketches and edit them',
            icon: <FiImage className="w-8 h-8" />,
            path: '/image-to-sketch',
            color: 'bg-green-500'
        },
        {
            title: 'Upload & Process',
            description: 'Upload CSV files and process them',
            icon: <FiUpload className="w-8 h-8" />,
            path: '/drawing',
            color: 'bg-purple-500'
        },
        {
            title: 'Download Results',
            description: 'Download your processed files',
            icon: <FiDownload className="w-8 h-8" />,
            path: '/drawing',
            color: 'bg-orange-500'
        }
    ];

    if (isLoading) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Header */}
            <header className="bg-white shadow-sm border-b">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-between items-center py-4">
                        <div className="flex items-center">
                            <h1 className="text-2xl font-bold text-gray-900">Adobe-GenSolve</h1>
                        </div>
                        <div className="flex items-center space-x-4">
                            <div className="flex items-center space-x-2">
                                <FiUser className="w-5 h-5 text-gray-400" />
                                <span className="text-gray-700">{user?.name || 'User'}</span>
                            </div>
                            <button
                                onClick={handleLogout}
                                className="flex items-center space-x-2 px-4 py-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
                            >
                                <FiLogOut className="w-4 h-4" />
                                <span>Logout</span>
                            </button>
                        </div>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                {/* Welcome Section */}
                <div className="mb-8">
                    <h2 className="text-3xl font-bold text-gray-900 mb-2">
                        Welcome back, {user?.name || 'User'}! 👋
                    </h2>
                    <p className="text-gray-600">
                        Ready to create something amazing? Choose from our powerful tools below.
                    </p>
                </div>

                {/* Features Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                    {features.map((feature, index) => (
                        <div
                            key={index}
                            onClick={() => navigate(feature.path)}
                            className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 cursor-pointer hover:shadow-md transition-shadow"
                        >
                            <div className={`${feature.color} text-white rounded-lg p-3 w-fit mb-4`}>
                                {feature.icon}
                            </div>
                            <h3 className="text-lg font-semibold text-gray-900 mb-2">
                                {feature.title}
                            </h3>
                            <p className="text-gray-600 text-sm">
                                {feature.description}
                            </p>
                        </div>
                    ))}
                </div>

                {/* Quick Actions */}
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <button
                            onClick={() => navigate('/drawing')}
                            className="flex items-center justify-center space-x-2 px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                        >
                            <FiEdit3 className="w-5 h-5" />
                            <span>Start Drawing</span>
                        </button>
                        <button
                            onClick={() => navigate('/image-to-sketch')}
                            className="flex items-center justify-center space-x-2 px-4 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                        >
                            <FiImage className="w-5 h-5" />
                            <span>Convert Image</span>
                        </button>
                        <button
                            onClick={() => navigate('/drawing')}
                            className="flex items-center justify-center space-x-2 px-4 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
                        >
                            <FiUpload className="w-5 h-5" />
                            <span>Upload CSV</span>
                        </button>
                    </div>
                </div>

                {/* Recent Activity */}
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
                    {recentDrawings.length > 0 ? (
                        <div className="space-y-4">
                            {recentDrawings.map((drawing, index) => (
                                <div key={index} className="flex items-center space-x-4 p-4 bg-gray-50 rounded-lg">
                                    <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                                        <FiEdit3 className="w-6 h-6 text-blue-600" />
                                    </div>
                                    <div className="flex-1">
                                        <h4 className="font-medium text-gray-900">{drawing.title}</h4>
                                        <p className="text-sm text-gray-600">{drawing.created_at}</p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="text-center py-8">
                            <FiEdit3 className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                            <p className="text-gray-600">No recent activity. Start creating!</p>
                        </div>
                    )}
                </div>
            </main>
        </div>
    );
};

export default Dashboard; 