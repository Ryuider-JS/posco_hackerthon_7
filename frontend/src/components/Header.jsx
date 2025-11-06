const Header = ({ title, subtitle }) => {
  return (
    <div className="bg-gradient-to-r from-[#7c4dff] to-[#9c27b0] text-white p-4 rounded-lg mb-4 shadow-sm">
      <div className="flex items-center justify-center">
        <span className="text-2xl mr-3">📸</span>
        <div>
          <h1 className="text-xl font-bold">{title}</h1>
          <p className="text-purple-100 text-sm mt-0.5">{subtitle}</p>
        </div>
      </div>
    </div>
  );
};

export default Header;
