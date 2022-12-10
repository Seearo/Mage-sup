from django.urls import path
from account.views import AccountView, AchievementsView, AddToBlacklistView, \
AddToBookmarksView, AddToFriendsView, \
BlacklistView, BookmarksView, BookmarksSortingView, \
DiaryConfirmRegistrationView, DiarySortingView, \
DiaryView, FriendsAcceptAllView, FriendsAutoAcceptAllView, \
FriendsAutoRejectAllView, FriendsClearCommentView, FriendsCommentingView, \
FriendsNoAutoView, FriendsRejectAllView, FriendsSortingView, FriendsView,\
MessagesSortingView, MessageView, MessageWritingView, ProfileView, \
ReceiveToFriendsView, RegisterToLessonView, RegisterToLesson2View, RegistrationView, \
RegistrationSortingView, RejectFromFriendsView, RemoveFromBlacklistView, \
RemoveFromBookmarksView, RemoveFromFriendsView, SettingsView, TimetableView, \
UnregisterView, UploadPhotoView, WantsToCoachView
from django.contrib.auth.views import LogoutView
from django.conf import settings
from django.conf.urls import url

urlpatterns = [
    path('account.html', AccountView.as_view()),
    path('achievements.html', AchievementsView.as_view()),
    path('blacklists<int:page>.html', BlacklistView.as_view()),
    path('blacklist.html', BlacklistView.as_view()),
    path('bookmarks<int:page>.html', BookmarksView.as_view()),
    path('bookmarks.html', BookmarksView.as_view()),
    #path('chatid1598737bi.html', ChatidView.as_view()),
    path('diary<int:page>.html', DiaryView.as_view()),
    path('diary.html', DiaryView.as_view()),
    path('friends<int:page>.html', FriendsView.as_view()),
    path('friends.html', FriendsView.as_view()),
    path('message<int:page>.html', MessageView.as_view()),
    path('message.html', MessageView.as_view()),
    path('profile.html/user_id<int:user_id>', ProfileView.as_view()),
    path('registration.html_coach_id<int:coach_id>', RegistrationView.as_view()),
    path('timetable.html', TimetableView.as_view()),

    path('add_to_blacklist/watched_user_id<int:watched_user_id>/next=<path:next_url>', AddToBlacklistView.as_view()),
    path('add_to_bookmarks/watched_user_id<int:watched_user_id>/next=<path:next_url>', AddToBookmarksView.as_view()),
    #path('add_to_bookmarks/watched_user_id<int:watched_user_id>', AddToBookmarksView.as_view()), # адреса с двойной переадресацией распознаются неверно
    path('add_to_friends/watched_user_id<int:watched_user_id>/next=<path:next_url>', AddToFriendsView.as_view()),
    path('bookmarks_sorting', BookmarksSortingView.as_view()),
    path('confirm_registration_id=<int:registration_id>_next=<path:next_url>', DiaryConfirmRegistrationView.as_view()),
    path('diary_sorting', DiarySortingView.as_view()),
    path('friends_accept_all_next=<path:next_url>', FriendsAcceptAllView.as_view()),
    path('friends_auto_accept_all_next=<path:next_url>', FriendsAutoAcceptAllView.as_view()),
    path('friends_auto_reject_all_next=<path:next_url>', FriendsAutoRejectAllView.as_view()),
    path('friends_clear_comment_friend_id=<int:friend_id>_next=<path:next_url>', FriendsClearCommentView.as_view()),
    path('friends_commenting_friend_id=<int:friend_id>_next=<path:next_url>', FriendsCommentingView.as_view()),  # POST
    path('friends_commenting<int:friend_id>.html', FriendsCommentingView.as_view()),  # GET
    path('friends_no_auto_next=<path:next_url>', FriendsNoAutoView.as_view()),
    path('friends_reject_all_next=<path:next_url>', FriendsRejectAllView.as_view()),
    path('friends_sorting', FriendsSortingView.as_view()),
    url(r'^logout/$', LogoutView.as_view(), {'next_page': settings.LOGOUT_REDIRECT_URL}, name='logout'),
    path('messages_sorting', MessagesSortingView.as_view()),
    path('message_writing_recipient_id=<int:recipient_id>_next=<path:next_url>', MessageWritingView.as_view()),  # POST
    path('message_writing<int:recipient_id>_page<int:page>.html', MessageWritingView.as_view()),  # GET
    path('receive_to_friends/watched_user_id<int:watched_user_id>/next=<path:next_url>', ReceiveToFriendsView.as_view()),
    path('register_coach_id<int:coach_id>_datetime_<str:year>_<str:month>_<str:day>_<str:hour>_<str:minute>', RegisterToLessonView.as_view()),
    path('register_one_day_coach_id<int:coach_id>', RegisterToLesson2View.as_view()),
    path('registration_sorting_coach_id<int:coach_id>', RegistrationSortingView.as_view()),
    path('reject_from_friends/watched_user_id<int:watched_user_id>/next=<path:next_url>', RejectFromFriendsView.as_view()),
    path('remove_from_blacklist/watched_user_id<int:watched_user_id>/next=<path:next_url>', RemoveFromBlacklistView.as_view()),
    path('remove_from_bookmarks/watched_user_id<int:watched_user_id>/next=<path:next_url>', RemoveFromBookmarksView.as_view()),
    path('remove_from_friends/watched_user_id<int:watched_user_id>/next=<path:next_url>', RemoveFromFriendsView.as_view()),
    path('settings', SettingsView.as_view()),
    path('unregister_registration_id<int:registration_id>_next_<path:next_url>', UnregisterView.as_view()),
    path('upload_photo', UploadPhotoView.as_view()),
    path('wants_to_coach', WantsToCoachView.as_view()),

]
