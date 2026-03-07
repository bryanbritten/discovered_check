interface Props {
  fullScreen?: boolean;
  size?: "sm" | "md" | "lg";
}

export default function LoadingSpinner({ fullScreen, size = "md" }: Props) {
  const sizes = { sm: "h-5 w-5", md: "h-8 w-8", lg: "h-12 w-12" };

  const spinner = (
    <div
      className={`${sizes[size]} animate-spin rounded-full border-2 border-chess-accent border-t-transparent`}
    />
  );

  if (fullScreen) {
    return (
      <div className="flex h-screen items-center justify-center bg-chess-dark">
        {spinner}
      </div>
    );
  }

  return <div className="flex items-center justify-center p-6">{spinner}</div>;
}
