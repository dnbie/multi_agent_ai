import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import toast from 'react-hot-toast';
import { agentAPI } from '../services/api';
import {
  Mail,
  FileText,
  Plane,
  Bus,
  Train,
  FolderOpen,
  Globe,
  Cloud,
  Newspaper,
  Bell,
  AlertTriangle,
  Send,
  Sparkles,
  History,
  CheckCircle,
  XCircle,
  Loader,
  Zap,
  Sun,
  CloudRain,
  Wind,
  Droplets,
  Thermometer,
  MapPin,
  Folder,
  HelpCircle,
  User,
  AtSign,
  Copy,
  ChevronDown,
  Phone,
  Shield,
  Siren,
  Heart,
  Flame,
  Navigation,
  ExternalLink,
  Map
} from 'lucide-react';

const AGENTS = [
  {
    id: 'email',
    name: 'Email Agent',
    description: 'Send emails, draft messages, and manage your inbox automatically.',
    icon: Mail,
    color: '#3b82f6',
    examples: [
      'Send email to boss@company.com about quarterly review',
      'Draft email to team about Friday meeting',
      'Send follow-up email to client regarding proposal'
    ]
  },
  {
    id: 'report',
    name: 'Report Generator',
    description: 'Generate professional reports, summaries, and documentation.',
    icon: FileText,
    color: '#8b5cf6',
    examples: [
      'Generate a report on monthly expenses',
      'Create a project status report for the team',
      'Write a detailed report on customer feedback'
    ]
  },
  {
    id: 'flight',
    name: 'Flight Search',
    description: 'Search, compare, and book flights across multiple airlines.',
    icon: Plane,
    color: '#06b6d4',
    examples: [
      'Search flights from DEL to BOM on 2026-04-15',
      'Find cheapest flights from Bangalore to Hyderabad',
      'Book flight from Chennai to Kolkata'
    ]
  },
  {
    id: 'bus',
    name: 'Bus Routes',
    description: 'Find bus schedules, routes, and book bus tickets easily.',
    icon: Bus,
    color: '#10b981',
    examples: [
      'Find buses from Mumbai to Pune tomorrow',
      'Search bus routes from Bangalore to Mysore',
      'Show bus schedules from Chennai to Coimbatore'
    ]
  },
  {
    id: 'train',
    name: 'Train Tickets',
    description: 'Search trains, check availability, and book railway tickets.',
    icon: Train,
    color: '#f59e0b',
    examples: [
      'Book train from Coimbatore to Chennai tomorrow',
      'Find trains from Delhi to Mumbai on 2026-04-10',
      'Search Rajdhani express from Delhi to Bangalore'
    ]
  },
  {
    id: 'file_organizer',
    name: 'File Organizer',
    description: 'Organize, rename, and manage your files automatically.',
    icon: FolderOpen,
    color: '#ec4899',
    examples: []
  },
  {
    id: 'browser',
    name: 'Browser Agent',
    description: 'Automate web browsing, searches, and online tasks.',
    icon: Globe,
    color: '#6366f1',
    examples: [
      'Play Shape of You by Ed Sheeran on YouTube',
      'Search for Python tutorials on Google',
      'Get directions from Coimbatore to Chennai on Maps'
    ]
  },
  {
    id: 'weather',
    name: 'Weather',
    description: 'Get weather forecasts, alerts, and climate information.',
    icon: Cloud,
    color: '#0ea5e9',
    examples: [
      'What is the weather in Chennai today?',
      'Show 3-day forecast for Mumbai',
      'Is it going to rain in Coimbatore tomorrow?'
    ]
  },
  {
    id: 'news',
    name: 'News Agent',
    description: 'Get the latest news, headlines, and trending stories.',
    icon: Newspaper,
    color: '#f43f5e',
    examples: [
      'Show today\'s top AI news headlines',
      'What are the latest technology news?',
      'Latest business and finance news'
    ]
  },
  {
    id: 'reminder',
    name: 'Reminders',
    description: 'Set reminders, alarms, and schedule notifications.',
    icon: Bell,
    color: '#a855f7',
    examples: [
      'Remind me to take medicine at 8 PM',
      'Set a reminder to call mom in 30 minutes',
      'Show all my pending reminders'
    ]
  },
  {
    id: 'emergency',
    name: 'Emergency',
    description: 'Emergency contacts, nearby hospitals, and urgent assistance.',
    icon: AlertTriangle,
    color: '#ef4444',
    examples: [
      'I met with an accident, need help',
      'Show emergency contacts and nearest hospitals',
      'Fire emergency, what should I do?'
    ]
  }
];

// Ticket colors for alternating list items
const TICKET_COLORS = [
  { bg: 'rgba(99, 102, 241, 0.15)', border: '#6366f1', accent: '#818cf8' },   // Indigo
  { bg: 'rgba(16, 185, 129, 0.15)', border: '#10b981', accent: '#34d399' },   // Emerald
  { bg: 'rgba(245, 158, 11, 0.15)', border: '#f59e0b', accent: '#fbbf24' },   // Amber
  { bg: 'rgba(236, 72, 153, 0.15)', border: '#ec4899', accent: '#f472b6' },   // Pink
  { bg: 'rgba(6, 182, 212, 0.15)', border: '#06b6d4', accent: '#22d3ee' },    // Cyan
  { bg: 'rgba(168, 85, 247, 0.15)', border: '#a855f7', accent: '#c084fc' },   // Purple
];

// ============== Razorpay Payment Handler ==============
const handleBookTicket = async (ticket, type, color) => {
  const rawFare = ticket.price || ticket.fare || ticket.cost || 0;
  const price = (typeof rawFare === 'object') ? Object.values(rawFare)[0] : rawFare;
  const name = ticket.name || ticket.flight_name || ticket.train_name || ticket.bus_name || ticket.operator || `${type} Ticket`;
  
  if (!price || price <= 0) {
    toast.error('Invalid ticket price');
    return;
  }

  try {
    // Create order on backend
    const orderResponse = await fetch('http://localhost:5000/api/payment/create-order', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('authToken')}`
      },
      body: JSON.stringify({
        amount: price,
        booking_type: type,
        booking_details: {
          ticket_name: name,
          departure: ticket.departure_time || ticket.time || ticket.dep || '',
          from: ticket.from || ticket.source || '',
          to: ticket.to || ticket.destination || ''
        }
      })
    });

    const orderData = await orderResponse.json();
    
    if (!orderData.success) {
      toast.error(orderData.message || 'Failed to create order');
      return;
    }

    // Open Razorpay checkout
    const options = {
      key: orderData.key_id,
      amount: orderData.amount_paise,
      currency: orderData.currency,
      name: 'Agent X',
      description: `${type.charAt(0).toUpperCase() + type.slice(1)} Booking - ${name}`,
      order_id: orderData.order_id,
      handler: async function (response) {
        // Verify payment on backend
        try {
          const verifyResponse = await fetch('http://localhost:5000/api/payment/verify', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${localStorage.getItem('authToken')}`
            },
            body: JSON.stringify({
              razorpay_order_id: response.razorpay_order_id,
              razorpay_payment_id: response.razorpay_payment_id,
              razorpay_signature: response.razorpay_signature
            })
          });

          const verifyData = await verifyResponse.json();
          
          if (verifyData.success) {
            toast.success('🎉 Payment successful! Ticket booked.');
          } else {
            toast.error('Payment verification failed');
          }
        } catch (err) {
          toast.error('Error verifying payment');
        }
      },
      prefill: {
        name: localStorage.getItem('user') ? JSON.parse(localStorage.getItem('user')).full_name : '',
        email: localStorage.getItem('user') ? JSON.parse(localStorage.getItem('user')).email : ''
      },
      theme: {
        color: color.border
      },
      modal: {
        ondismiss: function() {
          toast('Payment cancelled', { icon: '⚠️' });
        }
      }
    };

    const razorpay = new window.Razorpay(options);
    razorpay.open();

  } catch (error) {
    console.error('Payment error:', error);
    toast.error('Payment initialization failed');
  }
};

// ============== Ticket List Component ==============
const TicketList = ({ tickets, type }) => {
  if (!tickets || tickets.length === 0) {
    return (
      <div className="no-tickets">
        <p>No {type}s found for your search.</p>
      </div>
    );
  }

  return (
    <div className="ticket-list-container">
      <div className="ticket-controls">
        <span className="ticket-count">{tickets.length} {type}s found</span>
      </div>

      {/* Ticket List */}
      <div className="ticket-list">
        {tickets.map((ticket, idx) => {
          const color = TICKET_COLORS[idx % TICKET_COLORS.length];
          const name = ticket.name || ticket.flight_name || ticket.train_name || ticket.bus_name || ticket.operator || `${type} ${idx + 1}`;
          const time = ticket.time || ticket.departure_time || ticket.departure || ticket.dep || ticket.timing || '—';
          const rawFare = ticket.price || ticket.fare || ticket.cost || 0;
          const price = (typeof rawFare === 'object') 
            ? Object.values(rawFare)[0] 
            : rawFare;
          const seats = ticket.seats || ticket.seats_available || ticket.available_seats || ticket.availability 
            || (ticket.classes ? ticket.classes.join(', ') : '—');
          const duration = ticket.duration || '';
          const trainNo = ticket.train_no || '';
          
          return (
            <div 
              key={idx} 
              className="ticket-item"
              style={{ 
                background: color.bg, 
                borderLeftColor: color.border 
              }}
            >
              <div className="ticket-row">
                <div className="ticket-info">
                  <div className="ticket-name" style={{ color: color.accent }}>
                    {trainNo ? `${trainNo} — ` : ''}{name}
                  </div>
                  <div className="ticket-details">
                    <span className="ticket-time">
                      <span className="ticket-label">Departs</span>
                      <span className="ticket-value">{time}</span>
                    </span>
                    {duration && (
                      <span className="ticket-time">
                        <span className="ticket-label">Duration</span>
                        <span className="ticket-value">{duration}</span>
                      </span>
                    )}
                    <span className="ticket-price">
                      <span className="ticket-label">Price</span>
                      <span className="ticket-value">₹{typeof price === 'number' ? price.toLocaleString() : price}</span>
                    </span>
                    <span className="ticket-seats">
                      <span className="ticket-label">{ticket.classes ? 'Classes' : 'Seats'}</span>
                      <span className="ticket-value" style={{ color: color.border }}>{seats}</span>
                    </span>
                  </div>
                </div>
                <button 
                  className="book-btn"
                  style={{ 
                    background: color.border,
                    boxShadow: `0 4px 15px ${color.bg}`
                  }}
                  onClick={() => handleBookTicket(ticket, type, color)}
                >
                  Book Now
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

// ============== Weather Display Component ==============
const WeatherDisplay = ({ data }) => {
  // Extract weather data from various possible structures
  const current = data.current || data;
  const forecast = data.forecast || [];
  const advice = data.advice || data.ai_advice || '';
  
  // Handle both lowercase and capitalized field names from API
  const temp = current.temp || current.temperature || current.Temperature || current.temp_c || 0;
  const feelsLike = current.feels_like || current.feelslike || current['Feels like'] || current['Feels Like'] || temp;
  const humidity = current.humidity || current.Humidity || 0;
  const wind = current.wind_speed || current.wind || current['Wind speed'] || current['Wind Speed'] || current.wind_kph || 0;
  const description = current.description || current.Description || current.condition || current.weather || 'Clear';
  const city = current.city || current.City || data.city || 'Unknown';
  const country = current.country || current.Country || '';

  // Get weather icon based on description
  const getWeatherIcon = (desc) => {
    const d = desc.toLowerCase();
    if (d.includes('rain') || d.includes('drizzle')) return { icon: CloudRain, color: '#3b82f6', bg: 'rgba(59, 130, 246, 0.15)' };
    if (d.includes('cloud') || d.includes('overcast')) return { icon: Cloud, color: '#64748b', bg: 'rgba(100, 116, 139, 0.15)' };
    if (d.includes('haze') || d.includes('fog') || d.includes('mist')) return { icon: Wind, color: '#94a3b8', bg: 'rgba(148, 163, 184, 0.15)' };
    return { icon: Sun, color: '#f59e0b', bg: 'rgba(245, 158, 11, 0.15)' };
  };

  const weatherStyle = getWeatherIcon(description);
  const WeatherIcon = weatherStyle.icon;

  return (
    <div className="weather-display">
      {/* Main Weather Card */}
      <div className="weather-main" style={{ background: weatherStyle.bg, borderColor: weatherStyle.color }}>
        <div className="weather-icon-large">
          <WeatherIcon size={64} color={weatherStyle.color} />
        </div>
        <div className="weather-info-main">
          <div className="weather-location">
            <MapPin size={18} />
            <span>{city}{country ? `, ${country}` : ''}</span>
          </div>
          <div className="weather-temp">
            <span className="temp-value">{Math.round(temp)}°C</span>
            <span className="temp-feels">Feels like {Math.round(feelsLike)}°C</span>
          </div>
          <div className="weather-condition" style={{ color: weatherStyle.color }}>
            {description}
          </div>
        </div>
      </div>

      {/* Weather Stats Grid */}
      <div className="weather-stats">
        <div className="weather-stat" style={{ borderColor: '#3b82f6' }}>
          <Droplets size={24} color="#3b82f6" />
          <div className="stat-info">
            <span className="stat-value">{humidity}%</span>
            <span className="stat-label">Humidity</span>
          </div>
        </div>
        <div className="weather-stat" style={{ borderColor: '#06b6d4' }}>
          <Wind size={24} color="#06b6d4" />
          <div className="stat-info">
            <span className="stat-value">{wind} m/s</span>
            <span className="stat-label">Wind Speed</span>
          </div>
        </div>
        <div className="weather-stat" style={{ borderColor: '#f59e0b' }}>
          <Thermometer size={24} color="#f59e0b" />
          <div className="stat-info">
            <span className="stat-value">{Math.round(temp)}°C</span>
            <span className="stat-label">Temperature</span>
          </div>
        </div>
      </div>

      {/* AI Advice */}
      {advice && (
        <div className="weather-advice">
          <div className="advice-header">
            <Sparkles size={18} color="#a855f7" />
            <span>AI Recommendations</span>
          </div>
          <p>{advice}</p>
        </div>
      )}

      {/* Forecast */}
      {forecast && forecast.length > 0 && (
        <div className="weather-forecast">
          <h4>Forecast</h4>
          <div className="forecast-list">
            {forecast.slice(0, 5).map((day, idx) => {
              const dayStyle = getWeatherIcon(day.description || day.condition || '');
              const DayIcon = dayStyle.icon;
              return (
                <div key={idx} className="forecast-item" style={{ background: dayStyle.bg }}>
                  <span className="forecast-date">{day.date || `Day ${idx + 1}`}</span>
                  <DayIcon size={24} color={dayStyle.color} />
                  <span className="forecast-temp">{day.temp_max || day.temp || '—'}°</span>
                  <span className="forecast-desc" style={{ color: dayStyle.color }}>{day.description || day.condition || ''}</span>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

// ============== News Display Component ==============
const NewsDisplay = ({ data }) => {
  const articles = data.articles || data.news || data.headlines || [];
  
  if (!articles.length) {
    return <div className="no-data">No news articles found.</div>;
  }

  const categoryColors = {
    technology: '#6366f1',
    business: '#10b981',
    sports: '#f59e0b',
    entertainment: '#ec4899',
    health: '#ef4444',
    science: '#06b6d4',
    default: '#8b5cf6'
  };

  return (
    <div className="news-display">
      {articles.slice(0, 10).map((article, idx) => {
        const color = Object.values(categoryColors)[idx % Object.values(categoryColors).length];
        return (
          <div key={idx} className="news-item" style={{ borderLeftColor: color }}>
            <div className="news-source" style={{ color }}>{article.source || 'News'}</div>
            <h4 className="news-title">{article.title || article.headline}</h4>
            {article.description && <p className="news-desc">{article.description}</p>}
            {article.url && (
              <a href={article.url} target="_blank" rel="noopener noreferrer" className="news-link" style={{ color }}>
                Read more →
              </a>
            )}
          </div>
        );
      })}
    </div>
  );
};

// ============== Emergency Display Component ==============
const EmergencyDisplay = ({ data }) => {
  const contacts = data.contacts || data.emergency_contacts || [];
  const emergencyType = data.emergency_type || data.type || 'Emergency';
  const guidance = data.guidance || data.instructions || data.advice || '';
  const city = data.city || data.location || '';
  const hospitals = data.nearby_hospitals || data.hospitals || '';

  const getContactIcon = (name) => {
    const n = (name || '').toLowerCase();
    if (n.includes('police')) return { icon: Shield, color: '#3b82f6', bg: 'rgba(59, 130, 246, 0.15)' };
    if (n.includes('ambulance') || n.includes('medical')) return { icon: Heart, color: '#ef4444', bg: 'rgba(239, 68, 68, 0.15)' };
    if (n.includes('fire')) return { icon: Flame, color: '#f97316', bg: 'rgba(249, 115, 22, 0.15)' };
    if (n.includes('women')) return { icon: User, color: '#ec4899', bg: 'rgba(236, 72, 153, 0.15)' };
    if (n.includes('child')) return { icon: Heart, color: '#a855f7', bg: 'rgba(168, 85, 247, 0.15)' };
    if (n.includes('disaster')) return { icon: AlertTriangle, color: '#f59e0b', bg: 'rgba(245, 158, 11, 0.15)' };
    return { icon: Phone, color: '#10b981', bg: 'rgba(16, 185, 129, 0.15)' };
  };

  // Build Google Maps query for nearby hospitals
  const mapQuery = city 
    ? `hospitals+near+${encodeURIComponent(city)}` 
    : 'nearby+hospitals';

  return (
    <div className="emergency-display">
      {/* Emergency Header */}
      <div className="emergency-alert-banner">
        <div className="alert-icon-pulse">
          <Siren size={28} color="#ef4444" />
        </div>
        <div className="alert-info">
          <h3>{emergencyType.toUpperCase()}</h3>
          {city && <span className="alert-location"><MapPin size={14} /> {city}</span>}
        </div>
      </div>

      {/* Emergency Contacts Grid */}
      {contacts.length > 0 && (
        <div className="emergency-contacts-grid">
          <h4><Phone size={18} /> Emergency Contacts</h4>
          <div className="contacts-grid">
            {contacts.map((contact, idx) => {
              const style = getContactIcon(contact.name || contact.Name);
              const Icon = style.icon;
              const name = contact.name || contact.Name || 'Emergency';
              const number = contact.number || contact.Number || contact.phone || '';
              return (
                <div key={idx} className="emergency-contact-card" style={{ borderColor: style.color }}>
                  <div className="ec-icon" style={{ background: style.bg }}>
                    <Icon size={24} color={style.color} />
                  </div>
                  <div className="ec-info">
                    <span className="ec-name">{name}</span>
                    <a href={`tel:${number}`} className="ec-number" style={{ color: style.color }}>
                      {number}
                    </a>
                  </div>
                  <a href={`tel:${number}`} className="ec-call-btn" style={{ background: style.color }}>
                    <Phone size={16} />
                  </a>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Guidance Section */}
      {guidance && (
        <div className="emergency-guidance">
          <div className="guidance-header">
            <Shield size={20} color="#f59e0b" />
            <h4>Safety Guidance</h4>
          </div>
          <div className="guidance-steps">
            {guidance.split(/\d+\.\s*/).filter(Boolean).map((step, idx) => (
              <div key={idx} className="guidance-step">
                <span className="step-number">{idx + 1}</span>
                <p>{step.trim()}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Nearby Map */}
      <div className="emergency-map-section">
        <div className="map-header">
          <Map size={20} color="#10b981" />
          <h4>Nearby Hospitals & Emergency Services</h4>
        </div>
        <div className="map-container">
          <iframe
            title="Nearby Hospitals"
            width="100%"
            height="300"
            style={{ border: 0, borderRadius: '12px' }}
            loading="lazy"
            referrerPolicy="no-referrer-when-downgrade"
            src={`https://www.google.com/maps/embed/v1/search?key=AIzaSyBFw0Qbyq9zTFTd-tUY6dZWTgaQzuU17R8&q=${mapQuery}&zoom=13`}
          />
        </div>
        <div className="map-actions">
          <a 
            href={`https://www.google.com/maps/search/${mapQuery}`}
            target="_blank" 
            rel="noopener noreferrer"
            className="map-link-btn"
          >
            <Navigation size={16} />
            Open in Google Maps
            <ExternalLink size={14} />
          </a>
          <a 
            href={`https://www.google.com/maps/search/fire+station+near+${encodeURIComponent(city || 'me')}`}
            target="_blank" 
            rel="noopener noreferrer"
            className="map-link-btn fire"
          >
            <Flame size={16} />
            Nearby Fire Stations
            <ExternalLink size={14} />
          </a>
        </div>
      </div>
    </div>
  );
};

// ============== Result Display Component ==============
const ResultDisplay = ({ data, agent }) => {
  // Handle null/undefined data
  if (!data) {
    return (
      <div className="result-card">
        <p className="result-message">Task completed successfully!</p>
      </div>
    );
  }

  // If data is a string, display it nicely
  if (typeof data === 'string') {
    return (
      <div className="result-card">
        <p className="result-message">{data}</p>
      </div>
    );
  }

  // Extract common fields from result object
  const { success, message, data: nestedData } = data;
  const displayData = nestedData || data;

  // Format the main message
  const mainMessage = message || (success ? 'Task completed successfully!' : 'Task failed');

  // Check agent types for specialized display
  const ticketAgents = ['flight', 'bus', 'train'];
  const isTicketAgent = ticketAgents.includes(agent);
  const isWeatherAgent = agent === 'weather';
  const isNewsAgent = agent === 'news';
  const isEmergencyAgent = agent === 'emergency';
  
  // Try to find ticket array in the data
  const findTickets = (obj) => {
    if (!obj || typeof obj !== 'object') return null;
    
    // Direct array
    if (Array.isArray(obj)) return obj;
    
    // Look for common ticket array keys
    const ticketKeys = ['flights', 'buses', 'trains', 'results', 'options', 'tickets', 'data', 'all_flights', 'all_buses', 'all_trains'];
    for (const key of ticketKeys) {
      if (Array.isArray(obj[key])) return obj[key];
    }
    
    // Check nested data
    if (obj.data && typeof obj.data === 'object') {
      return findTickets(obj.data);
    }
    
    return null;
  };

  const tickets = isTicketAgent ? findTickets(displayData) : null;

  return (
    <div className="result-display">
      {/* Main Message Card */}
      <div className="result-card main-card">
        <div className="result-icon">
          {success !== false ? (
            <CheckCircle size={32} color="#10b981" />
          ) : (
            <XCircle size={32} color="#ef4444" />
          )}
        </div>
        <div className="result-main">
          <h4>{mainMessage}</h4>
          {agent && <span className="agent-badge">Processed by: {agent}</span>}
        </div>
      </div>

      {/* Specialized Displays based on agent type */}
      {isWeatherAgent && displayData && (
        <WeatherDisplay data={displayData} />
      )}

      {isNewsAgent && displayData && (
        <NewsDisplay data={displayData} />
      )}

      {/* Emergency Display */}
      {isEmergencyAgent && displayData && (
        <EmergencyDisplay data={displayData} />
      )}

      {/* Ticket List Display for booking agents */}
      {isTicketAgent && tickets && (
        <TicketList tickets={tickets} type={agent} />
      )}

      {/* Regular Structured Data Display for other agents */}
      {!isTicketAgent && !isWeatherAgent && !isNewsAgent && !isEmergencyAgent && displayData && typeof displayData === 'object' && (
        <div className="result-details">
          {Object.entries(displayData).map(([key, value]) => {
            // Skip internal/meta fields
            if (['success', 'error', 'message', 'timestamp'].includes(key)) return null;
            
            return (
              <ResultItem key={key} label={key} value={value} />
            );
          })}
        </div>
      )}
    </div>
  );
};

// Individual Result Item Component
const ResultItem = ({ label, value }) => {
  // Format the label to be human readable
  const formatLabel = (str) => {
    return str
      .replace(/_/g, ' ')
      .replace(/([A-Z])/g, ' $1')
      .replace(/^./, c => c.toUpperCase())
      .trim();
  };

  // Format value based on type
  const renderValue = (val) => {
    if (val === null || val === undefined) return <span className="empty-value">—</span>;
    
    if (typeof val === 'boolean') {
      return (
        <span className={`bool-value ${val ? 'true' : 'false'}`}>
          {val ? '✓ Yes' : '✗ No'}
        </span>
      );
    }
    
    if (typeof val === 'number') {
      return <span className="number-value">{val.toLocaleString()}</span>;
    }
    
    if (Array.isArray(val)) {
      if (val.length === 0) return <span className="empty-value">None</span>;
      return (
        <ul className="array-value">
          {val.slice(0, 10).map((item, idx) => (
            <li key={idx}>
              {typeof item === 'object' ? (
                <div className="nested-object">
                  {Object.entries(item).map(([k, v]) => (
                    <span key={k}><strong>{formatLabel(k)}:</strong> {String(v)}</span>
                  ))}
                </div>
              ) : (
                String(item)
              )}
            </li>
          ))}
          {val.length > 10 && <li className="more-items">+ {val.length - 10} more items</li>}
        </ul>
      );
    }
    
    if (typeof val === 'object') {
      return (
        <div className="nested-object">
          {Object.entries(val).map(([k, v]) => (
            <div key={k} className="nested-item">
              <span className="nested-label">{formatLabel(k)}:</span>
              <span className="nested-value">{typeof v === 'object' ? JSON.stringify(v) : String(v)}</span>
            </div>
          ))}
        </div>
      );
    }
    
    // String value - handle long text
    const strVal = String(val);
    if (strVal.length > 500) {
      return <p className="long-text">{strVal}</p>;
    }
    return <span>{strVal}</span>;
  };

  return (
    <div className="result-item">
      <div className="result-label">{formatLabel(label)}</div>
      <div className="result-value">{renderValue(value)}</div>
    </div>
  );
};

const Dashboard = ({ page }) => {
  const { agentType } = useParams();
  const navigate = useNavigate();
  const [selectedAgent, setSelectedAgent] = useState(agentType || null);
  const [task, setTask] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);

  // Sync selectedAgent with URL parameter when it changes
  useEffect(() => {
    setSelectedAgent(agentType || null);
    setTask('');
    setResult(null);
  }, [agentType]);

  const currentAgent = AGENTS.find(a => a.id === selectedAgent);

  const handleAgentSelect = (agentId) => {
    // Navigate to the agent's URL instead of just setting state
    navigate(`/agents/${agentId}`);
  };

  const handleBackToDashboard = () => {
    navigate('/dashboard');
  };

  const handleExampleClick = (example) => {
    setTask(example);
  };

  // Direct task execution (for email composer and similar)
  const executeDirectTask = async (directTask) => {
    if (!directTask.trim()) {
      toast.error('Please enter a task');
      return;
    }

    setLoading(true);
    setResult(null);

    try {
      const response = await agentAPI.executeTask(directTask, selectedAgent || 'auto');
      setResult({
        success: true,
        data: response.data.result,
        agent: response.data.agent_used,
        timestamp: new Date().toISOString()
      });
      
      setHistory(prev => [{
        task: directTask,
        agent: response.data.agent_used || selectedAgent || 'auto',
        timestamp: new Date().toISOString(),
        success: true,
        result: response.data.result
      }, ...prev].slice(0, 10));

      toast.success('Task completed successfully!');
    } catch (error) {
      setResult({
        success: false,
        error: error.response?.data?.message || 'Task execution failed',
        timestamp: new Date().toISOString()
      });
      toast.error('Task execution failed');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    if (!task.trim()) {
      toast.error('Please enter a task');
      return;
    }

    setLoading(true);
    setResult(null);

    try {
      const response = await agentAPI.executeTask(task, selectedAgent || 'auto');
      setResult({
        success: true,
        data: response.data.result,
        agent: response.data.agent_used,
        timestamp: new Date().toISOString()
      });
      
      setHistory(prev => [{
        task,
        agent: response.data.agent_used || selectedAgent || 'auto',
        timestamp: new Date().toISOString(),
        success: true,
        result: response.data.result
      }, ...prev].slice(0, 10));

      toast.success('Task completed successfully!');
    } catch (error) {
      setResult({
        success: false,
        error: error.response?.data?.message || 'Task execution failed',
        timestamp: new Date().toISOString()
      });
      toast.error('Task execution failed');
    } finally {
      setLoading(false);
    }
  };

  if (page === 'history') {
    return <HistoryPage history={history} />;
  }

  if (page === 'settings') {
    return <SettingsPage />;
  }

  return (
    <div className="dashboard">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="dashboard-header">
          <h1>
            {selectedAgent ? currentAgent?.name : 'Welcome to Agent X'}
          </h1>
          <p>
            {selectedAgent 
              ? currentAgent?.description 
              : 'Select an agent or use Auto mode to intelligently route your task'
            }
          </p>
        </div>

        {/* Agent Cards Grid */}
        {!selectedAgent && (
          <div className="agents-grid">
            {/* Auto Mode Card */}
            <motion.div
              className="agent-card"
              onClick={() => navigate('/agents/auto')}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              style={{ borderColor: '#6366f1' }}
            >
              <div 
                className="agent-icon" 
                style={{ background: 'linear-gradient(135deg, #6366f1, #8b5cf6)' }}
              >
                <Sparkles size={26} color="white" />
              </div>
              <h3>Auto Mode</h3>
              <p>Let AI intelligently select the best agent for your task.</p>
            </motion.div>

            {AGENTS.map((agent) => {
              const Icon = agent.icon;
              return (
                <motion.div
                  key={agent.id}
                  className="agent-card"
                  onClick={() => handleAgentSelect(agent.id)}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <div 
                    className="agent-icon" 
                    style={{ background: `${agent.color}20`, color: agent.color }}
                  >
                    <Icon size={26} />
                  </div>
                  <h3>{agent.name}</h3>
                  <p>{agent.description}</p>
                </motion.div>
              );
            })}
          </div>
        )}

        {/* Task Input Section */}
        {selectedAgent && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="task-section"
          >
            <div style={{ 
              display: 'flex', 
              justifyContent: 'space-between', 
              alignItems: 'center',
              marginBottom: '1rem'
            }}>
              <h2>
                <Zap size={20} />
                Enter Your Task
              </h2>
              <button 
                className="btn btn-secondary"
                onClick={handleBackToDashboard}
              >
                ← Back to Agents
              </button>
            </div>

            {/* Email Composer UI */}
            {selectedAgent === 'email' && (
              <div className="email-composer">
                <div className="email-composer-header">
                  <Mail size={24} color="#3b82f6" />
                  <h3>Email Composer</h3>
                </div>
                
                <div className="email-form">
                  <div className="email-row">
                    <div className="email-field flex-2">
                      <label>
                        <AtSign size={14} /> To Email <span className="required">*</span>
                      </label>
                      <input
                        type="email"
                        id="emailTo"
                        placeholder="recipient@example.com"
                        className="email-input"
                      />
                    </div>
                    <div className="email-field flex-1">
                      <label>
                        <Copy size={14} /> CC (optional)
                      </label>
                      <input
                        type="email"
                        id="emailCc"
                        placeholder="cc@example.com"
                        className="email-input"
                      />
                    </div>
                  </div>
                  
                  <div className="email-field">
                    <label>
                      <Sparkles size={14} /> Subject <span className="required">*</span>
                    </label>
                    <input
                      type="text"
                      id="emailSubject"
                      placeholder="Enter email subject..."
                      className="email-input"
                    />
                  </div>
                  
                  <div className="email-field">
                    <label>
                      <User size={14} /> Your Name (for signature)
                      <span className="help-icon" title="This will appear in your email signature">
                        <HelpCircle size={14} />
                      </span>
                    </label>
                    <input
                      type="text"
                      id="emailSenderName"
                      placeholder="Your name"
                      className="email-input"
                      defaultValue={localStorage.getItem('user') ? JSON.parse(localStorage.getItem('user')).full_name : ''}
                    />
                  </div>
                  
                  <div className="email-row">
                    <button 
                      className="btn generate-body-btn"
                      onClick={async () => {
                        const subject = document.getElementById('emailSubject').value;
                        const tone = document.getElementById('emailTone').value;
                        const to = document.getElementById('emailTo').value;
                        const sender = document.getElementById('emailSenderName').value || 'User';
                        
                        if (!subject) {
                          toast.error('Please enter a subject first');
                          return;
                        }
                        
                        const body = document.getElementById('emailBody');
                        body.value = 'Generating email...';
                        body.disabled = true;
                        
                        // Extract recipient name from email or use Sir/Madam
                        let recipientName = to ? to.split('@')[0].replace(/[._]/g, ' ').replace(/\b\w/g, l => l.toUpperCase()) : '';
                        const hasNumbers = /\d/.test(recipientName);
                        const greeting = hasNumbers || !recipientName ? 'Hi Sir/Madam,' : `Hi ${recipientName},`;
                        
                        try {
                          const response = await agentAPI.executeTask(
                            `Generate a ${tone.toLowerCase()} email body for subject: "${subject}". Only return the main content text without any greeting or signature.`,
                            'email'
                          );
                          
                          // Debug: log the full response structure
                          console.log('Email API Response:', JSON.stringify(response.data, null, 2));
                          
                          const result = response.data.result;
                          
                          // Try all possible paths to find the body content
                          let generatedContent = '';
                          
                          // Try result.data.body first (most likely path)
                          if (result?.data?.body && result.data.body.length > 10) {
                            generatedContent = result.data.body;
                          }
                          // Try result.data.content
                          else if (result?.data?.content && result.data.content.length > 10) {
                            generatedContent = result.data.content;
                          }
                          // Try result.body directly
                          else if (result?.body && result.body.length > 10) {
                            generatedContent = result.body;
                          }
                          // Fallback: generate a simple body based on subject
                          else {
                            generatedContent = `I hope this email finds you well.\n\nI wanted to reach out regarding ${subject}.\n\nPlease let me know if you have any questions or need further information.`;
                          }
                          
                          // Clean up LLM artifacts - remove greeting/signature the LLM adds
                          generatedContent = generatedContent
                            .replace(/^Dear\s+(Recipient|Sir|Madam|Sir\/Madam)[,.]?\s*/i, '')
                            .replace(/^Hi\s+(Recipient|Sir|Madam|Sir\/Madam|there)[,.]?\s*/i, '')
                            .replace(/\n*(Best\s+regards|Warm\s+regards|Kind\s+regards|Regards|Sincerely|Thanks|Thank\s+you)[,.]?\s*\n*\[?(Your\s+Name|Agent\s*X|Sender)[\/\w\s]*\]?\s*$/gi, '')
                            .replace(/\[Your\s+Name[\/\w\s]*\]/gi, '')
                            .replace(/\[Agent\s*X\]/gi, '')
                            .trim();
                          
                          // Construct full email with greeting and signature
                          const fullBody = `${greeting}\n\n${generatedContent}\n\nBest Regards,\n${sender}`;
                          body.value = fullBody;
                          toast.success('Email generated! Review, edit if needed, then click Send Email.');
                        } catch (error) {
                          toast.error('Failed to generate email body');
                          body.value = '';
                        } finally {
                          body.disabled = false;
                        }
                      }}
                    >
                      <Sparkles size={16} />
                      Generate Body
                    </button>
                    
                    <div className="tone-selector">
                      <label>Tone</label>
                      <div className="select-wrapper">
                        <select id="emailTone" className="tone-select">
                          <option value="Professional">Professional</option>
                          <option value="Friendly">Friendly</option>
                          <option value="Formal">Formal</option>
                          <option value="Casual">Casual</option>
                        </select>
                        <ChevronDown size={16} className="select-icon" />
                      </div>
                    </div>
                  </div>
                  
                  <div className="email-field">
                    <label>
                      <FileText size={14} /> Email Body <span className="optional-hint">(auto-generated if empty)</span>
                    </label>
                    <textarea
                      id="emailBody"
                      className="email-body-input"
                      placeholder="Leave empty to auto-generate based on subject, or type your message here..."
                      rows={6}
                    />
                  </div>
                  
                  <button 
                    className="btn btn-primary send-email-btn"
                    onClick={() => {
                      const to = document.getElementById('emailTo').value;
                      const cc = document.getElementById('emailCc').value;
                      const subject = document.getElementById('emailSubject').value;
                      const body = document.getElementById('emailBody').value;
                      
                      if (!to) {
                        toast.error('Please enter recipient email');
                        return;
                      }
                      if (!subject) {
                        toast.error('Please enter email subject');
                        return;
                      }
                      if (!body.trim()) {
                        toast.error('Please generate or write an email body first');
                        return;
                      }
                      
                      const emailTask = `Send email to ${to}${cc ? ` cc ${cc}` : ''} with subject "${subject}" and body: ${body}`;
                      executeDirectTask(emailTask);
                    }}
                    disabled={loading}
                  >
                    {loading ? <Loader size={18} className="spinning" /> : <Send size={18} />}
                    {loading ? 'Sending...' : 'Send Email'}
                  </button>
                </div>
              </div>
            )}

            {/* File Organizer - Folder Path Picker (shows for file_organizer or auto mode) */}
            {(selectedAgent === 'file_organizer' || selectedAgent === 'auto') && (
              <div className={`folder-picker-section ${selectedAgent === 'auto' ? 'auto-mode' : ''}`}>
                <div className="folder-picker-header">
                  <Folder size={20} color="#ec4899" />
                  <span>{selectedAgent === 'auto' ? 'Organize Files (File Organizer)' : 'Select Folder to Organize'}</span>
                  {selectedAgent === 'auto' && (
                    <span className="optional-badge">Optional</span>
                  )}
                </div>
                <p className="folder-picker-desc">
                  {selectedAgent === 'auto' 
                    ? 'Browse a folder or use quick paths to organize files.'
                    : 'Browse a folder from your computer or use quick paths below.'}
                </p>
                
                {/* Browse Folder Button + Path Display */}
                <div className="folder-browse-section">
                  <input
                    type="file"
                    id="folderBrowseInput"
                    webkitdirectory=""
                    directory=""
                    style={{ display: 'none' }}
                    onChange={(e) => {
                      const files = e.target.files;
                      if (files && files.length > 0) {
                        // Extract folder path from the first file's webkitRelativePath
                        const relativePath = files[0].webkitRelativePath;
                        const folderName = relativePath.split('/')[0];
                        
                        // Set the folder name in the path input
                        const pathInput = document.getElementById('folderPath');
                        pathInput.value = folderName;
                        setTask(`Organize files in folder: ${folderName}`);
                        toast.success(`Folder selected: ${folderName} (${files.length} files found)`);
                      }
                      // Reset so same folder can be re-selected
                      e.target.value = '';
                    }}
                  />
                  <button 
                    className="btn browse-folder-btn"
                    onClick={() => document.getElementById('folderBrowseInput').click()}
                  >
                    <FolderOpen size={18} />
                    Browse Folder
                  </button>
                  
                  <div className="folder-path-display">
                    <input
                      type="text"
                      className="folder-path-input"
                      placeholder="No folder selected — browse or use quick paths"
                      id="folderPath"
                      onChange={(e) => {
                        if (e.target.value) {
                          setTask(`Organize files in folder: ${e.target.value}`);
                        }
                      }}
                    />
                  </div>
                  
                  <button 
                    className="btn btn-primary organize-btn"
                    onClick={() => {
                      const folderPath = document.getElementById('folderPath').value;
                      if (folderPath) {
                        setTask(`Organize files in folder: ${folderPath}`);
                        handleSubmit();
                      } else {
                        toast.error('Please select a folder first');
                      }
                    }}
                    disabled={loading}
                  >
                    {loading ? <Loader size={16} className="spinning" /> : <Sparkles size={16} />}
                    {loading ? 'Organizing...' : 'Organize'}
                  </button>
                </div>

                <div className="folder-picker-hints">
                  <span className="hint-label">Quick paths:</span>
                  <button 
                    className="path-chip" 
                    onClick={() => {
                      const username = localStorage.getItem('user') ? JSON.parse(localStorage.getItem('user')).full_name?.split(' ')[0] || 'User' : 'User';
                      document.getElementById('folderPath').value = `C:\\Users\\${username}\\Downloads`;
                      setTask(`Organize files in folder: C:\\Users\\${username}\\Downloads`);
                    }}
                  >
                    📥 Downloads
                  </button>
                  <button 
                    className="path-chip" 
                    onClick={() => {
                      const username = localStorage.getItem('user') ? JSON.parse(localStorage.getItem('user')).full_name?.split(' ')[0] || 'User' : 'User';
                      document.getElementById('folderPath').value = `C:\\Users\\${username}\\Documents`;
                      setTask(`Organize files in folder: C:\\Users\\${username}\\Documents`);
                    }}
                  >
                    📄 Documents
                  </button>
                  <button 
                    className="path-chip" 
                    onClick={() => {
                      const username = localStorage.getItem('user') ? JSON.parse(localStorage.getItem('user')).full_name?.split(' ')[0] || 'User' : 'User';
                      document.getElementById('folderPath').value = `C:\\Users\\${username}\\Desktop`;
                      setTask(`Organize files in folder: C:\\Users\\${username}\\Desktop`);
                    }}
                  >
                    🖥️ Desktop
                  </button>
                  <button 
                    className="path-chip" 
                    onClick={() => {
                      const username = localStorage.getItem('user') ? JSON.parse(localStorage.getItem('user')).full_name?.split(' ')[0] || 'User' : 'User';
                      document.getElementById('folderPath').value = `C:\\Users\\${username}\\Pictures`;
                      setTask(`Organize files in folder: C:\\Users\\${username}\\Pictures`);
                    }}
                  >
                    🖼️ Pictures
                  </button>
                </div>
              </div>
            )}

            {/* Task Input - hide for email agent since it has Email Composer */}
            {selectedAgent !== 'email' && (
              <div className="task-input-wrapper">
                <textarea
                  className="task-input"
                  placeholder={
                    selectedAgent === 'auto' 
                      ? "Describe your task and I'll route it to the best agent..."
                      : selectedAgent === 'file_organizer'
                      ? "Enter folder path above or type your organization request..."
                      : `What would you like the ${currentAgent?.name} to do?`
                  }
                  value={task}
                  onChange={(e) => setTask(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && e.ctrlKey) {
                      handleSubmit();
                    }
                  }}
                />
                <button 
                  className="btn btn-primary task-submit-btn"
                  onClick={handleSubmit}
                  disabled={loading || !task.trim()}
                >
                  {loading ? (
                    <Loader size={18} className="spinning" />
                  ) : (
                    <>
                      <Send size={18} />
                      Execute
                    </>
                  )}
                </button>
              </div>
            )}

            {/* Examples - hide for file_organizer and email since they have custom UI */}
            {selectedAgent && selectedAgent !== 'file_organizer' && selectedAgent !== 'email' && (
              <div className="examples-section">
                <h4>Try these examples:</h4>
                <div className="examples-list">
                  {selectedAgent === 'auto' ? (
                    // Auto mode examples - diverse tasks
                    <>
                      <button className="example-chip" onClick={() => handleExampleClick('Send an email to team@company.com about the project update')}>
                        Send an email to team@company.com about the project update
                      </button>
                      <button className="example-chip" onClick={() => handleExampleClick('What is the weather in Mumbai today?')}>
                        What is the weather in Mumbai today?
                      </button>
                      <button className="example-chip" onClick={() => handleExampleClick('Search flights from Delhi to Bangalore tomorrow')}>
                        Search flights from Delhi to Bangalore tomorrow
                      </button>
                      <button className="example-chip" onClick={() => handleExampleClick('Show me today\'s top technology news')}>
                        Show me today's top technology news
                      </button>
                      <button className="example-chip" onClick={() => handleExampleClick('Remind me to call mom at 6 PM')}>
                        Remind me to call mom at 6 PM
                      </button>
                      <button className="example-chip" onClick={() => handleExampleClick('Generate a report on quarterly sales performance')}>
                        Generate a report on quarterly sales performance
                      </button>
                    </>
                  ) : (
                    currentAgent?.examples?.map((example, idx) => (
                      <button
                        key={idx}
                        className="example-chip"
                        onClick={() => handleExampleClick(example)}
                      >
                        {example}
                      </button>
                    ))
                  )}
                </div>
              </div>
            )}
          </motion.div>
        )}

        {/* Result Section */}
        <AnimatePresence>
          {result && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="result-section"
            >
              <div className="result-header">
                <h3>
                  {result.success ? (
                    <CheckCircle size={20} color="#10b981" />
                  ) : (
                    <XCircle size={20} color="#ef4444" />
                  )}
                  Result
                </h3>
                <span className={`status-badge ${result.success ? 'success' : 'error'}`}>
                  {result.success ? 'Success' : 'Failed'}
                </span>
              </div>
              
              {result.success ? (
                <ResultDisplay data={result.data} agent={result.agent} />
              ) : (
                <div className="result-error">
                  <XCircle size={48} color="#ef4444" />
                  <h4>Something went wrong</h4>
                  <p>{result.error || 'An unexpected error occurred'}</p>
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </div>
  );
};

// History Page Component
const HistoryPage = ({ history }) => {
  const [expandedIdx, setExpandedIdx] = useState(null);
  
  const agentColors = {
    weather: '#3b82f6',
    news: '#8b5cf6',
    email: '#10b981',
    flight: '#f59e0b',
    train: '#06b6d4',
    bus: '#ec4899',
    report: '#ef4444',
    reminder: '#f97316',
    file_organizer: '#a855f7',
    browser: '#14b8a6',
    emergency: '#dc2626',
    auto: '#6366f1'
  };
  
  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1><History size={28} /> Task History</h1>
        <p>View your recent task executions and their results</p>
      </div>
      
      <div className="result-section">
        {history.length === 0 ? (
          <div className="empty-history">
            <History size={48} color="var(--text-muted)" />
            <p>No tasks executed yet</p>
            <span>Start by selecting an agent!</span>
          </div>
        ) : (
          <div className="history-list">
            {history.map((item, idx) => {
              const isExpanded = expandedIdx === idx;
              const color = agentColors[item.agent] || '#6366f1';
              
              return (
                <motion.div 
                  key={idx}
                  className={`history-item ${isExpanded ? 'expanded' : ''}`}
                  style={{ borderLeftColor: color }}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.05 }}
                >
                  <div 
                    className="history-header"
                    onClick={() => setExpandedIdx(isExpanded ? null : idx)}
                  >
                    <div className="history-info">
                      <span className="history-agent" style={{ color }}>
                        {item.agent?.toUpperCase() || 'AUTO'}
                      </span>
                      <span className="history-task">{item.task}</span>
                    </div>
                    <div className="history-meta">
                      <span className={`status-badge ${item.success ? 'success' : 'error'}`}>
                        {item.success ? '✓ Success' : '✗ Failed'}
                      </span>
                      <span className="history-time">
                        {new Date(item.timestamp).toLocaleString()}
                      </span>
                      <span className={`expand-icon ${isExpanded ? 'rotated' : ''}`}>
                        ▼
                      </span>
                    </div>
                  </div>
                  
                  <AnimatePresence>
                    {isExpanded && item.result && (
                      <motion.div
                        className="history-result"
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.3 }}
                      >
                        <div className="result-preview">
                          <ResultDisplay data={item.result} agent={item.agent} />
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </motion.div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

// Settings Page Component
const SettingsPage = () => {
  const [settings, setSettings] = useState({
    emergencyContacts: [
      { name: '', phone: '', relation: '' }
    ],
    preferredCity: '',
    emailNotifications: true,
    darkMode: true,
    language: 'en'
  });
  const [saved, setSaved] = useState(false);

  // Load settings from localStorage
  useEffect(() => {
    const savedSettings = localStorage.getItem('agentx_settings');
    if (savedSettings) {
      setSettings(JSON.parse(savedSettings));
    }
  }, []);

  const handleSave = () => {
    localStorage.setItem('agentx_settings', JSON.stringify(settings));
    setSaved(true);
    toast.success('Settings saved successfully!');
    setTimeout(() => setSaved(false), 2000);
  };

  const addEmergencyContact = () => {
    if (settings.emergencyContacts.length < 5) {
      setSettings(prev => ({
        ...prev,
        emergencyContacts: [...prev.emergencyContacts, { name: '', phone: '', relation: '' }]
      }));
    }
  };

  const removeEmergencyContact = (idx) => {
    setSettings(prev => ({
      ...prev,
      emergencyContacts: prev.emergencyContacts.filter((_, i) => i !== idx)
    }));
  };

  const updateEmergencyContact = (idx, field, value) => {
    setSettings(prev => ({
      ...prev,
      emergencyContacts: prev.emergencyContacts.map((contact, i) => 
        i === idx ? { ...contact, [field]: value } : contact
      )
    }));
  };

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>⚙️ Settings</h1>
        <p>Configure your profile and preferences</p>
      </div>
      
      {/* Emergency Contacts Section */}
      <motion.div 
        className="settings-section"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div className="section-header">
          <div className="section-title">
            <AlertTriangle size={24} color="#ef4444" />
            <h2>Emergency Contacts</h2>
          </div>
          <p>Add contacts for emergency alerts. These will be notified when you use the Emergency Agent.</p>
        </div>
        
        <div className="emergency-contacts-list">
          {settings.emergencyContacts.map((contact, idx) => (
            <div key={idx} className="contact-card">
              <div className="contact-number">{idx + 1}</div>
              <div className="contact-fields">
                <div className="field-group">
                  <label>Name</label>
                  <input
                    type="text"
                    placeholder="Contact name"
                    value={contact.name}
                    onChange={(e) => updateEmergencyContact(idx, 'name', e.target.value)}
                  />
                </div>
                <div className="field-group">
                  <label>Phone Number</label>
                  <input
                    type="tel"
                    placeholder="+91 XXXXX XXXXX"
                    value={contact.phone}
                    onChange={(e) => updateEmergencyContact(idx, 'phone', e.target.value)}
                  />
                </div>
                <div className="field-group">
                  <label>Relation</label>
                  <select
                    value={contact.relation}
                    onChange={(e) => updateEmergencyContact(idx, 'relation', e.target.value)}
                  >
                    <option value="">Select relation</option>
                    <option value="parent">Parent</option>
                    <option value="spouse">Spouse</option>
                    <option value="sibling">Sibling</option>
                    <option value="friend">Friend</option>
                    <option value="colleague">Colleague</option>
                    <option value="other">Other</option>
                  </select>
                </div>
              </div>
              {settings.emergencyContacts.length > 1 && (
                <button 
                  className="remove-contact-btn"
                  onClick={() => removeEmergencyContact(idx)}
                >
                  ✕
                </button>
              )}
            </div>
          ))}
        </div>
        
        {settings.emergencyContacts.length < 5 && (
          <button className="add-contact-btn" onClick={addEmergencyContact}>
            + Add Emergency Contact
          </button>
        )}
      </motion.div>

      {/* Preferences Section */}
      <motion.div 
        className="settings-section"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <div className="section-header">
          <div className="section-title">
            <Zap size={24} color="#f59e0b" />
            <h2>Preferences</h2>
          </div>
          <p>Customize your Agent X experience</p>
        </div>
        
        <div className="preferences-grid">
          <div className="preference-item">
            <div className="pref-info">
              <span className="pref-label">Default City</span>
              <span className="pref-desc">For weather and local news</span>
            </div>
            <input
              type="text"
              className="pref-input"
              placeholder="Mumbai, Delhi, etc."
              value={settings.preferredCity}
              onChange={(e) => setSettings(prev => ({ ...prev, preferredCity: e.target.value }))}
            />
          </div>
          
          <div className="preference-item">
            <div className="pref-info">
              <span className="pref-label">Email Notifications</span>
              <span className="pref-desc">Receive task summaries via email</span>
            </div>
            <label className="toggle">
              <input
                type="checkbox"
                checked={settings.emailNotifications}
                onChange={(e) => setSettings(prev => ({ ...prev, emailNotifications: e.target.checked }))}
              />
              <span className="toggle-slider"></span>
            </label>
          </div>
          
          <div className="preference-item">
            <div className="pref-info">
              <span className="pref-label">Language</span>
              <span className="pref-desc">Select preferred language</span>
            </div>
            <select
              className="pref-select"
              value={settings.language}
              onChange={(e) => setSettings(prev => ({ ...prev, language: e.target.value }))}
            >
              <option value="en">English</option>
              <option value="hi">हिंदी (Hindi)</option>
              <option value="ta">தமிழ் (Tamil)</option>
              <option value="te">తెలుగు (Telugu)</option>
              <option value="ml">മലയാളം (Malayalam)</option>
            </select>
          </div>
        </div>
      </motion.div>

      {/* Save Button */}
      <motion.div 
        className="settings-actions"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
      >
        <button 
          className={`save-settings-btn ${saved ? 'saved' : ''}`}
          onClick={handleSave}
        >
          {saved ? '✓ Saved!' : 'Save Settings'}
        </button>
      </motion.div>
    </div>
  );
};

export default Dashboard;
