

const CustomAlert = ({ message, onClose }: { message: string, onClose: () => void }) => {
  return (
    <div className="alert-backdrop">
      <div className="alert-box">
        <p>{message}</p>
        <button onClick={onClose}>OK</button>
      </div>
    </div>
  );
};

export default CustomAlert;
