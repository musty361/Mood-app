import React, { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const MOODS = [
  { value: 1, emoji: "😢", label: "Very Sad", color: "bg-red-500" },
  { value: 2, emoji: "😕", label: "Sad", color: "bg-orange-500" },
  { value: 3, emoji: "😐", label: "Neutral", color: "bg-yellow-500" },
  { value: 4, emoji: "🙂", label: "Happy", color: "bg-green-500" },
  { value: 5, emoji: "😊", label: "Very Happy", color: "bg-blue-500" }
];

function App() {
  const [currentView, setCurrentView] = useState('today');
  const [selectedMood, setSelectedMood] = useState(null);
  const [notes, setNotes] = useState('');
  const [moodEntries, setMoodEntries] = useState([]);
  const [todayMood, setTodayMood] = useState(null);
  const [currentMonth, setCurrentMonth] = useState(new Date());
  const [isLoading, setIsLoading] = useState(false);

  const today = new Date().toISOString().split('T')[0];

  useEffect(() => {
    fetchMoodEntries();
    fetchTodayMood();
  }, []);

  const fetchMoodEntries = async () => {
    try {
      setIsLoading(true);
      const response = await axios.get(`${API}/moods`);
      setMoodEntries(response.data);
    } catch (error) {
      console.error('Error fetching mood entries:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchTodayMood = async () => {
    try {
      const response = await axios.get(`${API}/moods/${today}`);
      if (response.data) {
        setTodayMood(response.data);
        setSelectedMood(response.data.mood);
        setNotes(response.data.notes || '');
      }
    } catch (error) {
      // No mood entry for today yet
      setTodayMood(null);
    }
  };

  const saveMood = async () => {
    if (!selectedMood) {
      alert('Please select a mood first!');
      return;
    }

    try {
      setIsLoading(true);
      const moodData = {
        mood: selectedMood,
        mood_emoji: MOODS.find(m => m.value === selectedMood)?.emoji,
        notes: notes,
        date: today
      };

      if (todayMood) {
        // Update existing mood
        await axios.put(`${API}/moods/${todayMood.id}`, moodData);
      } else {
        // Create new mood entry
        await axios.post(`${API}/moods`, moodData);
      }

      await fetchMoodEntries();
      await fetchTodayMood();
      alert('Mood saved successfully! 🎉');
    } catch (error) {
      console.error('Error saving mood:', error);
      alert('Error saving mood. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const exportData = async () => {
    try {
      setIsLoading(true);
      const response = await axios.get(`${API}/moods/export/csv`);
      
      // Create and download file
      const blob = new Blob([response.data.content], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = response.data.filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      
      alert('Data exported successfully! 📊');
    } catch (error) {
      console.error('Error exporting data:', error);
      alert('Error exporting data. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const renderTodayView = () => (
    <div className="max-w-md mx-auto space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-800 mb-2">How are you feeling today?</h2>
        <p className="text-gray-600">{new Date().toLocaleDateString('en-US', { 
          weekday: 'long', 
          year: 'numeric', 
          month: 'long', 
          day: 'numeric' 
        })}</p>
      </div>

      <div className="grid grid-cols-5 gap-3">
        {MOODS.map((mood) => (
          <button
            key={mood.value}
            onClick={() => setSelectedMood(mood.value)}
            className={`p-4 rounded-2xl transition-all duration-200 transform hover:scale-105 ${
              selectedMood === mood.value
                ? `${mood.color} ring-4 ring-offset-2 ring-indigo-300 shadow-lg`
                : 'bg-gray-100 hover:bg-gray-200'
            }`}
          >
            <div className="text-3xl mb-1">{mood.emoji}</div>
            <div className="text-xs font-medium text-gray-700">{mood.label}</div>
          </button>
        ))}
      </div>

      {selectedMood && (
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Add a note (optional)
            </label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="What happened today? How do you feel?"
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 resize-none"
              rows={3}
            />
          </div>

          <button
            onClick={saveMood}
            disabled={isLoading}
            className="w-full bg-indigo-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? 'Saving...' : (todayMood ? 'Update Mood' : 'Save Mood')}
          </button>
        </div>
      )}
    </div>
  );

  const renderHistoryView = () => (
    <div className="max-w-2xl mx-auto">
      <h2 className="text-2xl font-bold text-gray-800 mb-6 text-center">Mood History</h2>
      
      {moodEntries.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-6xl mb-4">📊</div>
          <p className="text-gray-600">No mood entries yet. Start tracking your mood today!</p>
        </div>
      ) : (
        <div className="space-y-3">
          {moodEntries.map((entry) => {
            const mood = MOODS.find(m => m.value === entry.mood);
            return (
              <div key={entry.id} className="bg-white rounded-lg shadow-md p-4 border-l-4 border-indigo-500">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <span className="text-3xl">{mood?.emoji}</span>
                    <div>
                      <div className="font-medium text-gray-900">{mood?.label}</div>
                      <div className="text-sm text-gray-500">
                        {new Date(entry.date).toLocaleDateString('en-US', {
                          weekday: 'short',
                          month: 'short',
                          day: 'numeric',
                          year: 'numeric'
                        })}
                      </div>
                    </div>
                  </div>
                  <div className={`w-3 h-3 rounded-full ${mood?.color}`}></div>
                </div>
                {entry.notes && (
                  <div className="mt-3 p-3 bg-gray-50 rounded-md">
                    <p className="text-sm text-gray-700 italic">"{entry.notes}"</p>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );

  const renderCalendarView = () => {
    const daysInMonth = new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1, 0).getDate();
    const firstDayOfMonth = new Date(currentMonth.getFullYear(), currentMonth.getMonth(), 1).getDay();
    const monthName = currentMonth.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });

    const getMoodForDate = (day) => {
      const dateStr = `${currentMonth.getFullYear()}-${String(currentMonth.getMonth() + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
      return moodEntries.find(entry => entry.date === dateStr);
    };

    const changeMonth = (increment) => {
      setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() + increment, 1));
    };

    return (
      <div className="max-w-md mx-auto">
        <div className="flex items-center justify-between mb-6">
          <button
            onClick={() => changeMonth(-1)}
            className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
          >
            ←
          </button>
          <h2 className="text-xl font-bold text-gray-800">{monthName}</h2>
          <button
            onClick={() => changeMonth(1)}
            className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
          >
            →
          </button>
        </div>

        <div className="grid grid-cols-7 gap-1 mb-2">
          {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
            <div key={day} className="text-center text-sm font-medium text-gray-500 py-2">
              {day}
            </div>
          ))}
        </div>

        <div className="grid grid-cols-7 gap-1">
          {[...Array(firstDayOfMonth)].map((_, i) => (
            <div key={i} className="h-10"></div>
          ))}
          
          {[...Array(daysInMonth)].map((_, i) => {
            const day = i + 1;
            const moodEntry = getMoodForDate(day);
            const mood = moodEntry ? MOODS.find(m => m.value === moodEntry.mood) : null;
            
            return (
              <div
                key={day}
                className="h-10 flex items-center justify-center relative rounded-lg hover:bg-gray-100 transition-colors"
              >
                <span className="text-sm font-medium">{day}</span>
                {mood && (
                  <div className="absolute -top-1 -right-1 text-lg">
                    {mood.emoji}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">
            <span className="text-5xl mr-2">🌙</span>
            Moodify
          </h1>
          <p className="text-gray-600">Track your daily emotions and discover patterns</p>
        </div>

        {/* Navigation */}
        <div className="flex justify-center mb-8">
          <div className="bg-white rounded-xl p-1 shadow-lg">
            <button
              onClick={() => setCurrentView('today')}
              className={`px-6 py-2 rounded-lg font-medium transition-colors ${
                currentView === 'today'
                  ? 'bg-indigo-600 text-white shadow-md'
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              Today
            </button>
            <button
              onClick={() => setCurrentView('history')}
              className={`px-6 py-2 rounded-lg font-medium transition-colors ${
                currentView === 'history'
                  ? 'bg-indigo-600 text-white shadow-md'
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              History
            </button>
            <button
              onClick={() => setCurrentView('calendar')}
              className={`px-6 py-2 rounded-lg font-medium transition-colors ${
                currentView === 'calendar'
                  ? 'bg-indigo-600 text-white shadow-md'
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              Calendar
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="bg-white rounded-2xl shadow-xl p-8 mb-8">
          {currentView === 'today' && renderTodayView()}
          {currentView === 'history' && renderHistoryView()}
          {currentView === 'calendar' && renderCalendarView()}
        </div>

        {/* Export Button */}
        <div className="text-center">
          <button
            onClick={exportData}
            disabled={isLoading || moodEntries.length === 0}
            className="inline-flex items-center px-6 py-3 bg-green-600 text-white font-medium rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span className="mr-2">📊</span>
            Export Data (CSV)
          </button>
        </div>

        {/* Loading Overlay */}
        {isLoading && (
          <div className="fixed inset-0 bg-black bg-opacity-25 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 shadow-xl">
              <div className="flex items-center space-x-3">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-indigo-600"></div>
                <span className="text-gray-700">Loading...</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;