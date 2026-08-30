import { useState, useEffect } from 'react';
import axios from 'axios';

export function useNotifications() {
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    // We assume session_id is generated and stored in localStorage
    const sessionId = localStorage.getItem('groww_session_id') || crypto.randomUUID();
    if (!localStorage.getItem('groww_session_id')) {
      localStorage.setItem('groww_session_id', sessionId);
    }

    const fetchNotifications = async () => {
      try {
        const response = await axios.get(`http://localhost:8000/api/data/notifications?session_id=${sessionId}`);
        if (response.data && response.data.notifications) {
          setNotifications(response.data.notifications);
          setUnreadCount(response.data.notifications.length); // Just a simple unread count based on total returned
        }
      } catch (error) {
        console.error("Failed to fetch notifications", error);
      }
    };

    fetchNotifications();
    const interval = setInterval(fetchNotifications, 60000); // 60s
    return () => clearInterval(interval);
  }, []);

  const markAllRead = () => {
    setUnreadCount(0);
    // Ideally we would send a request to the backend to mark them as read, but 
    // for this demo we'll just clear the local unread count.
  };

  return { notifications, unreadCount, markAllRead };
}
