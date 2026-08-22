/**
 * pages/community/Community.jsx
 * Screen 10 - Community Page.
 * Feed from GET /api/community/posts (each post now includes
 * `is_liked_by_me` so the like button renders filled/unfilled correctly
 * on load, not just after a click), "Share your experience" composer
 * (POST /api/community/posts), like toggling (POST /api/community/posts/
 * <id>/like), and an expandable comment thread per post backed by
 * GET/POST /api/community/posts/<id>/comments.
 */
import { useEffect, useState } from "react";
import toast from "react-hot-toast";
import { Heart, MessageCircle, Send, UserCircle, Users, ChevronDown, ChevronUp } from "lucide-react";
import api from "../../configs/api";
import { useSelector } from "react-redux";
import { useBreadcrumb } from "../../lib/useBreadcrumb";
import { getErrorMessage, formatDate } from "../../lib/formatters";
import SearchToolbar from "../../components/SearchToolbar";
import EmptyState from "../../components/EmptyState";
import Loader from "../../components/Loader";

export default function Community() {
  useBreadcrumb([{ label: "Community" }]);
  const currentUser = useSelector((state) => state.auth.user);

  const [search, setSearch] = useState("");
  const [sortBy, setSortBy] = useState("recent");
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [newPost, setNewPost] = useState("");
  const [posting, setPosting] = useState(false);

  const loadPosts = () => {
    setLoading(true);
    api
      .get("/api/community/posts", { params: { search: search || undefined, sort_by: sortBy } })
      .then(({ data }) => setPosts(data.data))
      .catch((err) => toast.error(getErrorMessage(err, "Could not load the community feed.")))
      .finally(() => setLoading(false));
  };

  useEffect(loadPosts, [search, sortBy]);

  const handleShare = async (e) => {
    e.preventDefault();
    if (!newPost.trim()) return;
    setPosting(true);
    try {
      const { data } = await api.post("/api/community/posts", { content: newPost.trim() });
      setNewPost("");
      toast.success("Shared with the community!");
      // Prepend locally instead of a full reload so composing feels instant.
      setPosts((prev) => [{ ...data.data, comments: [] }, ...prev]);
    } catch (err) {
      toast.error(getErrorMessage(err, "Could not share your post."));
    } finally {
      setPosting(false);
    }
  };

  // Optimistic like toggle: flip the heart + count immediately, then
  // reconcile with whatever the server actually persisted. This is what
  // makes the heart appear filled right away instead of waiting on a
  // full feed refetch (and it keeps working even if that refetch fails).
  const handleLike = async (postId) => {
    setPosts((prev) =>
      prev.map((p) =>
        p.id === postId
          ? { ...p, is_liked_by_me: !p.is_liked_by_me, like_count: p.like_count + (p.is_liked_by_me ? -1 : 1) }
          : p
      )
    );
    try {
      const { data } = await api.post(`/api/community/posts/${postId}/like`);
      setPosts((prev) =>
        prev.map((p) => (p.id === postId ? { ...p, is_liked_by_me: data.data.liked, like_count: data.data.like_count } : p))
      );
    } catch (err) {
      toast.error(getErrorMessage(err, "Could not update like."));
      loadPosts(); // roll back to the real server state
    }
  };

  return (
    <div className="space-y-6 max-w-3xl mx-auto">
      <div>
        <h1 className="text-xl font-bold text-slate-800 dark:text-slate-100">Community</h1>
        <p className="text-sm text-slate-500 dark:text-slate-400">Trip stories, tips, and recommendations from fellow travelers.</p>
      </div>

      {/* Composer */}
      <form onSubmit={handleShare} className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-4 flex items-start gap-3">
        {currentUser?.profile_photo_url ? (
          <img src={currentUser.profile_photo_url} alt="" className="h-9 w-9 rounded-full object-cover shrink-0" />
        ) : (
          <UserCircle size={36} className="text-slate-300 shrink-0" />
        )}
        <div className="flex-1 flex items-center gap-2">
          <input
            value={newPost}
            onChange={(e) => setNewPost(e.target.value)}
            placeholder="Share a travel experience or recommendation..."
            className="flex-1 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-sky-500"
          />
          <button type="submit" disabled={posting || !newPost.trim()} className="inline-flex items-center gap-1.5 rounded-lg bg-sky-600 hover:bg-sky-700 text-white text-sm font-medium px-3 py-2 disabled:opacity-50">
            <Send size={14} /> Share
          </button>
        </div>
      </form>

      <SearchToolbar
        search={search}
        onSearchChange={setSearch}
        searchPlaceholder="Search posts by city, activity, or topic..."
        sortOptions={[
          { value: "recent", label: "Most Recent" },
          { value: "popular", label: "Most Liked" },
        ]}
        sortBy={sortBy}
        onSortByChange={setSortBy}
      />

      {loading ? (
        <Loader label="Loading the feed..." />
      ) : posts.length === 0 ? (
        <EmptyState icon={Users} title="No posts yet" description="Be the first to share a travel story." />
      ) : (
        <div className="space-y-4">
          {posts.map((post) => (
            <PostCard key={post.id} post={post} onLike={() => handleLike(post.id)} />
          ))}
        </div>
      )}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* PostCard - one feed item, with a like button and a lazily-loaded,   */
/* expandable comment thread.                                          */
/* ------------------------------------------------------------------ */
function PostCard({ post, onLike }) {
  const [commentsOpen, setCommentsOpen] = useState(false);
  const [comments, setComments] = useState(null); // null = not loaded yet
  const [loadingComments, setLoadingComments] = useState(false);
  const [commentText, setCommentText] = useState("");
  const [commentCount, setCommentCount] = useState(post.comment_count);
  const [submittingComment, setSubmittingComment] = useState(false);

  const toggleComments = async () => {
    const opening = !commentsOpen;
    setCommentsOpen(opening);
    if (opening && comments === null) {
      setLoadingComments(true);
      try {
        const { data } = await api.get(`/api/community/posts/${post.id}/comments`);
        setComments(data.data);
      } catch (err) {
        toast.error(getErrorMessage(err, "Could not load comments."));
        setComments([]);
      } finally {
        setLoadingComments(false);
      }
    }
  };

  const handleAddComment = async (e) => {
    e.preventDefault();
    if (!commentText.trim()) return;
    setSubmittingComment(true);
    try {
      const { data } = await api.post(`/api/community/posts/${post.id}/comments`, { content: commentText.trim() });
      setComments((prev) => [...(prev || []), data.data]);
      setCommentCount((c) => c + 1);
      setCommentText("");
    } catch (err) {
      toast.error(getErrorMessage(err, "Could not post your comment."));
    } finally {
      setSubmittingComment(false);
    }
  };

  return (
    <article className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-4">
      <div className="flex items-center gap-3 mb-2">
        {post.user?.profile_photo_url ? (
          <img src={post.user.profile_photo_url} alt="" className="h-9 w-9 rounded-full object-cover" />
        ) : (
          <UserCircle size={36} className="text-slate-300" />
        )}
        <div>
          <p className="text-sm font-semibold text-slate-800 dark:text-slate-100">{post.user?.full_name || "GlobeTrotter user"}</p>
          <p className="text-xs text-slate-400">{formatDate(post.created_at)}</p>
        </div>
        {post.category && (
          <span className="ml-auto text-xs rounded-full bg-sky-50 dark:bg-sky-900/40 text-sky-700 dark:text-sky-300 px-2 py-0.5">
            {post.category}
          </span>
        )}
      </div>
      <p className="text-sm text-slate-700 dark:text-slate-200 whitespace-pre-wrap">{post.content}</p>
      {post.image_url && <img src={post.image_url} alt="" className="mt-3 rounded-lg max-h-72 w-full object-cover" />}

      <div className="flex items-center gap-4 mt-3 text-xs text-slate-500 dark:text-slate-400">
        <button
          onClick={onLike}
          className={`flex items-center gap-1.5 transition-colors ${post.is_liked_by_me ? "text-rose-500" : "hover:text-rose-500"}`}
        >
          <Heart size={14} fill={post.is_liked_by_me ? "currentColor" : "none"} /> {post.like_count}
        </button>
        <button onClick={toggleComments} className="flex items-center gap-1.5 hover:text-sky-600 dark:hover:text-sky-400">
          <MessageCircle size={14} /> {commentCount}
          {commentsOpen ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
        </button>
      </div>

      {commentsOpen && (
        <div className="mt-3 pt-3 border-t border-slate-100 dark:border-slate-800 space-y-3">
          {loadingComments ? (
            <Loader label="Loading comments..." />
          ) : comments && comments.length > 0 ? (
            <ul className="space-y-2">
              {comments.map((c) => (
                <li key={c.id} className="flex items-start gap-2">
                  {c.user?.profile_photo_url ? (
                    <img src={c.user.profile_photo_url} alt="" className="h-7 w-7 rounded-full object-cover shrink-0" />
                  ) : (
                    <UserCircle size={28} className="text-slate-300 shrink-0" />
                  )}
                  <div className="min-w-0 rounded-lg bg-slate-50 dark:bg-slate-800 px-3 py-1.5 flex-1">
                    <p className="text-xs font-semibold text-slate-700 dark:text-slate-200">{c.user?.full_name || "GlobeTrotter user"}</p>
                    <p className="text-sm text-slate-600 dark:text-slate-300 whitespace-pre-wrap">{c.content}</p>
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-slate-400 dark:text-slate-500">No comments yet - be the first to reply.</p>
          )}

          <form onSubmit={handleAddComment} className="flex items-center gap-2">
            <input
              value={commentText}
              onChange={(e) => setCommentText(e.target.value)}
              placeholder="Write a comment..."
              className="flex-1 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 px-3 py-1.5 text-sm outline-none focus:ring-2 focus:ring-sky-500"
            />
            <button
              type="submit"
              disabled={submittingComment || !commentText.trim()}
              className="inline-flex items-center gap-1 rounded-lg bg-sky-600 hover:bg-sky-700 text-white text-xs font-medium px-3 py-1.5 disabled:opacity-50"
            >
              <Send size={12} /> Post
            </button>
          </form>
        </div>
      )}
    </article>
  );
}
