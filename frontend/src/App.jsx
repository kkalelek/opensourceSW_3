import { useEffect, useMemo, useState } from "react";

function App() {
  const [mode, setMode] = useState("range"); // now / range
  const [day, setDay] = useState("MON");
  const [start, setStart] = useState("00:00");
  const [end, setEnd] = useState("00:00");

  const [rooms, setRooms] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("시간을 선택하고 조회하세요.");

  const BASE_URL = "http://127.0.0.1:8000";
  const BUILDING = "IT융합대학";

  const dayLabel = {
    MON: "월요일",
    TUE: "화요일",
    WED: "수요일",
    THU: "목요일",
    FRI: "금요일",
  };

  const statusText = {
    green: "사용 가능",
    yellow: "곧 수업 시작",
    white: "현재 사용 중",
  };

  const statusColor = {
    green: "#d4edda",
    yellow: "#fff3cd",
    white: "#f8d7da",
  };

  const fetchNow = async () => {
    setLoading(true);
    setMessage("현재 강의실 정보를 불러오는 중...");
    try {
      const res = await fetch(
        `${BASE_URL}/api/buildings/${BUILDING}/available-now`
      );
      const data = await res.json();

      setRooms(data.rooms || []);
      setMessage(
        `${data.day || ""} ${data.query_time || ""} 기준 ${
          data.rooms?.length || 0
        }개 강의실`
      );
    } catch (error) {
      setRooms([]);
      setMessage("현재 조회에 실패했습니다.");
    } finally {
      setLoading(false);
    }
  };

  const fetchRange = async () => {
    if (start >= end) {
      setMessage("종료 시간은 시작 시간보다 늦어야 합니다.");
      return;
    }

    setLoading(true);
    setMessage("시간대 강의실 정보를 불러오는 중...");

    try {
      const url =
        `${BASE_URL}/api/buildings/${BUILDING}/available-range` +
        `?day=${day}&start=${start}&end=${end}`;

      const res = await fetch(url);
      const data = await res.json();

      setRooms(data.rooms || []);
      setMessage(
        `${dayLabel[day]} ${start} ~ ${end} 사용 가능한 강의실 ${
          data.rooms?.length || 0
        }개`
      );
    } catch (error) {
      setRooms([]);
      setMessage("시간 선택 조회에 실패했습니다.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRange();
  }, []);

  const handleSearch = () => {
    if (mode === "now") {
      fetchNow();
    } else {
      fetchRange();
    }
  };

  const stats = useMemo(() => {
    let green = 0;
    let yellow = 0;
    let white = 0;

    rooms.forEach((room) => {
      if (room.status === "green") green++;
      else if (room.status === "yellow") yellow++;
      else if (room.status === "white") white++;
    });

    return { green, yellow, white };
  }, [rooms]);

  return (
    <div
      style={{
        minHeight: "100vh",
        backgroundColor: "#f4f6f8",
        padding: "30px",
        fontFamily: "Arial, sans-serif",
      }}
    >
      <div
        style={{
          maxWidth: "1100px",
          margin: "0 auto",
          backgroundColor: "white",
          padding: "30px",
          borderRadius: "20px",
          boxShadow: "0 10px 30px rgba(0,0,0,0.08)",
        }}
      >
        <h1 style={{ textAlign: "center", marginBottom: "10px" }}>
          IT융합대학 빈 강의실 조회
        </h1>

        <p style={{ textAlign: "center", color: "#666", marginBottom: "25px" }}>
          현재 시간 조회 또는 원하는 시간대를 선택해 강의실을 확인하세요.
        </p>

        {/* 탭 */}
        <div
          style={{
            display: "flex",
            gap: "10px",
            marginBottom: "20px",
            justifyContent: "center",
          }}
        >
          <button
            onClick={() => setMode("now")}
            style={{
              padding: "10px 18px",
              border: "none",
              borderRadius: "10px",
              cursor: "pointer",
              backgroundColor: mode === "now" ? "#2563eb" : "#e5e7eb",
              color: mode === "now" ? "white" : "#111",
            }}
          >
            현재 조회
          </button>

          <button
            onClick={() => setMode("range")}
            style={{
              padding: "10px 18px",
              border: "none",
              borderRadius: "10px",
              cursor: "pointer",
              backgroundColor: mode === "range" ? "#2563eb" : "#e5e7eb",
              color: mode === "range" ? "white" : "#111",
            }}
          >
            시간 선택 조회
          </button>
        </div>

        {/* 검색 영역 */}
        <div
          style={{
            display: "flex",
            flexWrap: "wrap",
            gap: "12px",
            alignItems: "center",
            justifyContent: "center",
            marginBottom: "20px",
          }}
        >
          {mode === "range" && (
            <>
              <select
                value={day}
                onChange={(e) => setDay(e.target.value)}
                style={inputStyle}
              >
                <option value="MON">월요일</option>
                <option value="TUE">화요일</option>
                <option value="WED">수요일</option>
                <option value="THU">목요일</option>
                <option value="FRI">금요일</option>
              </select>

              <input
                type="time"
                value={start}
                onChange={(e) => setStart(e.target.value)}
                style={inputStyle}
              />

              <input
                type="time"
                value={end}
                onChange={(e) => setEnd(e.target.value)}
                style={inputStyle}
              />
            </>
          )}

          <button
            onClick={handleSearch}
            style={{
              padding: "11px 20px",
              backgroundColor: "#16a34a",
              color: "white",
              border: "none",
              borderRadius: "10px",
              cursor: "pointer",
              fontWeight: "bold",
            }}
          >
            조회하기
          </button>
        </div>

        {/* 안내 문구 */}
        <div
          style={{
            backgroundColor: "#f9fafb",
            padding: "12px",
            borderRadius: "10px",
            marginBottom: "20px",
            color: "#444",
          }}
        >
          {message}
        </div>

        {/* 현재 조회 통계 */}
        {mode === "now" && rooms.length > 0 && (
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))",
              gap: "12px",
              marginBottom: "20px",
            }}
          >
            <StatCard title="사용 가능" value={stats.green} color="#d4edda" />
            <StatCard title="곧 수업 시작" value={stats.yellow} color="#fff3cd" />
            <StatCard title="현재 사용 중" value={stats.white} color="#f8d7da" />
          </div>
        )}

        {/* 카드 목록 */}
        {loading ? (
          <p>불러오는 중...</p>
        ) : rooms.length === 0 ? (
          <p>조회된 강의실이 없습니다.</p>
        ) : (
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
              gap: "15px",
            }}
          >
            {rooms.map((room, index) => {
              const bg =
                mode === "range"
                  ? "#d4edda"
                  : statusColor[room.status] || "#eee";

              const label =
                mode === "range"
                  ? "사용 가능"
                  : statusText[room.status] || "확인 필요";

              return (
                <div
                  key={index}
                  style={{
                    backgroundColor: bg,
                    padding: "18px",
                    borderRadius: "14px",
                    boxShadow: "0 4px 10px rgba(0,0,0,0.06)",
                  }}
                >
                  <h3
                    style={{
                      marginTop: 0,
                      marginBottom: "10px",
                      fontSize: "18px",
                    }}
                  >
                    {room.room}
                  </h3>

                  <p style={{ margin: "6px 0", fontWeight: "bold" }}>
                    상태: {label}
                  </p>

                  {mode === "now" && room.current_course_name && (
                    <p style={{ margin: "6px 0" }}>
                      현재 수업: {room.current_course_name}
                    </p>
                  )}

                  {mode === "now" && room.current_class_end && (
                    <p style={{ margin: "6px 0" }}>
                      종료 시간: {room.current_class_end}
                    </p>
                  )}

                  {room.next_course_name && (
                    <p style={{ margin: "6px 0" }}>
                      다음 수업: {room.next_course_name}
                    </p>
                  )}

                  {room.next_class_start && (
                    <p style={{ margin: "6px 0" }}>
                      시작 시간: {room.next_class_start}
                    </p>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}

function StatCard({ title, value, color }) {
  return (
    <div
      style={{
        backgroundColor: color,
        padding: "16px",
        borderRadius: "12px",
      }}
    >
      <div style={{ fontSize: "14px", color: "#555" }}>{title}</div>
      <div style={{ fontSize: "26px", fontWeight: "bold" }}>{value}</div>
    </div>
  );
}

const inputStyle = {
  padding: "10px",
  borderRadius: "10px",
  border: "1px solid #ccc",
};

export default App;